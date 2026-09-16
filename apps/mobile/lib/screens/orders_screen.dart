import 'package:flutter/material.dart';

import '../data/demo_data.dart';
import '../models/app_models.dart';
import '../widgets/common_widgets.dart';

class OrdersScreen extends StatefulWidget {
  const OrdersScreen({super.key});

  @override
  State<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends State<OrdersScreen> {
  bool _showActive = true;

  @override
  Widget build(BuildContext context) {
    final orders = filmOrders.where((order) => _showActive ? order.status != OrderStatus.completed : order.status == OrderStatus.completed).toList();
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 24),
      children: [
        SegmentedButton<bool>(
          segments: const [ButtonSegment(value: true, label: Text('Active orders'), icon: Icon(Icons.timelapse_rounded)), ButtonSegment(value: false, label: Text('Completed'), icon: Icon(Icons.check_circle_outline_rounded))],
          selected: {_showActive},
          showSelectedIcon: false,
          onSelectionChanged: (selection) => setState(() => _showActive = selection.first),
        ),
        const SizedBox(height: 18),
        ...orders.map((order) => Padding(padding: const EdgeInsets.only(bottom: 11), child: _OrderCard(order: order))),
      ],
    );
  }
}

class _OrderCard extends StatelessWidget {
  const _OrderCard({required this.order});
  final FilmOrder order;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: () => _showDetails(context),
        child: Padding(
          padding: const EdgeInsets.all(15),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [Expanded(child: Text(order.id, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w900))), StatusChip(status: order.status)]),
              const SizedBox(height: 10),
              Text(order.lab, style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 3),
              Text('${order.service} · ${order.rolls} roll${order.rolls > 1 ? 's' : ''}'),
              const Divider(height: 24),
              Row(children: [const Icon(Icons.update_rounded, size: 16), const SizedBox(width: 6), Expanded(child: Text('Updated ${order.updatedAt}', style: const TextStyle(fontSize: 11))), const Icon(Icons.chevron_right_rounded)]),
            ],
          ),
        ),
      ),
    );
  }

  void _showDetails(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (context) => _OrderTimeline(order: order),
    );
  }
}

class _OrderTimeline extends StatelessWidget {
  const _OrderTimeline({required this.order});
  final FilmOrder order;

  @override
  Widget build(BuildContext context) {
    final currentIndex = OrderStatus.values.indexOf(order.status);
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(order.id, style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 3), Text(order.lab)])), StatusChip(status: order.status)]),
            const SizedBox(height: 22),
            Text('Order timeline', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),
            ...OrderStatus.values.map((status) {
              final index = OrderStatus.values.indexOf(status);
              final reached = index <= currentIndex;
              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Column(children: [Container(width: 24, height: 24, decoration: BoxDecoration(shape: BoxShape.circle, color: reached ? Theme.of(context).colorScheme.primary : const Color(0xFFE1E6E3)), child: Icon(reached ? Icons.check_rounded : Icons.more_horiz_rounded, color: reached ? Colors.white : const Color(0xFF7D8782), size: 15)), if (index < OrderStatus.values.length - 1) Container(width: 2, height: 28, color: reached && index < currentIndex ? Theme.of(context).colorScheme.primary : const Color(0xFFE1E6E3))]),
                  const SizedBox(width: 12),
                  Expanded(child: Padding(padding: const EdgeInsets.only(top: 3), child: Text(status.label, style: TextStyle(fontSize: 12, fontWeight: reached ? FontWeight.w800 : FontWeight.w500, color: reached ? const Color(0xFF26302C) : const Color(0xFF8A9490))))),
                ],
              );
            }),
            const SizedBox(height: 18),
            SizedBox(width: double.infinity, child: OutlinedButton.icon(onPressed: () => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Film Lab contact options opened.'))), icon: const Icon(Icons.chat_bubble_outline_rounded), label: const Text('Contact Film Lab'))),
          ],
        ),
      ),
    );
  }
}

