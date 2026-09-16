import 'package:flutter/material.dart';

import '../data/demo_data.dart';
import '../models/app_models.dart';
import '../theme/app_theme.dart';
import '../widgets/common_widgets.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _searchController = TextEditingController();
  String _selectedFormat = 'All';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final query = _searchController.text.toLowerCase();
    final labs = filmLabs.where((lab) {
      final matchesText = '${lab.name} ${lab.location}'.toLowerCase().contains(query);
      final matchesFormat = _selectedFormat == 'All' || lab.formats.contains(_selectedFormat);
      return matchesText && matchesFormat;
    }).toList();

    return SafeArea(
      top: false,
      child: ListView(
        padding: const EdgeInsets.fromLTRB(16, 14, 16, 24),
        children: [
          Text('Good afternoon, Khanh', style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 5),
          const Text('Find a trusted Film Lab and follow every roll from pickup to scan delivery.'),
          const SizedBox(height: 18),
          TextField(
            controller: _searchController,
            onChanged: (_) => setState(() {}),
            decoration: const InputDecoration(
              hintText: 'Search Film Labs or districts',
              prefixIcon: Icon(Icons.search_rounded),
              suffixIcon: Icon(Icons.tune_rounded),
            ),
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: 34,
            child: ListView(
              scrollDirection: Axis.horizontal,
              children: ['All', '35mm', '120', 'B&W'].map((format) {
                final selected = format == _selectedFormat;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(format),
                    selected: selected,
                    onSelected: (_) => setState(() => _selectedFormat = format),
                    labelStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700),
                    visualDensity: VisualDensity.compact,
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 22),
          _CurrentOrderCard(onTap: () => _showOrder(context)),
          const SizedBox(height: 22),
          SectionHeader(title: 'Recommended Film Labs', action: 'Map view', onAction: () => _showMessage(context, 'Map view will use the current city and filters.')),
          const SizedBox(height: 10),
          if (labs.isEmpty)
            const _NoResults()
          else
            ...labs.map((lab) => Padding(
              padding: const EdgeInsets.only(bottom: 11),
              child: _FilmLabCard(lab: lab, onTap: () => _showLab(context, lab)),
            )),
          const SizedBox(height: 10),
          const SectionHeader(title: 'Quick access'),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(child: _QuickAction(icon: Icons.auto_awesome_rounded, label: 'AI Assistant', color: const Color(0xFF76518E), onTap: () => _showAssistant(context))),
              const SizedBox(width: 10),
              Expanded(child: _QuickAction(icon: Icons.groups_2_outlined, label: 'Community', color: const Color(0xFFB85D43), onTap: () => _showMessage(context, 'Community feed opened.'))),
            ],
          ),
        ],
      ),
    );
  }

  void _showLab(BuildContext context, FilmLab lab) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (context) => _LabDetails(lab: lab),
    );
  }

  void _showOrder(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (context) => const _OrderPreview(),
    );
  }

  void _showAssistant(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (context) => const _AssistantSheet(),
    );
  }

  void _showMessage(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }
}

class _CurrentOrderCard extends StatelessWidget {
  const _CurrentOrderCard({required this.onTap});
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(15),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Expanded(child: Text('Current order', style: TextStyle(fontWeight: FontWeight.w800))),
                  const StatusChip(status: OrderStatus.processing),
                ],
              ),
              const SizedBox(height: 12),
              const Text('FL-2048 · Saigon Grain Lab', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
              const SizedBox(height: 4),
              const Text('Develop + Scan XL · 2 rolls'),
              const SizedBox(height: 15),
              Row(
                children: List.generate(6, (index) => Expanded(
                  child: Container(
                    height: 5,
                    margin: EdgeInsets.only(right: index == 5 ? 0 : 5),
                    decoration: BoxDecoration(
                      color: index < 3 ? AppTheme.teal : const Color(0xFFE1E6E3),
                      borderRadius: BorderRadius.circular(3),
                    ),
                  ),
                )),
              ),
              const SizedBox(height: 8),
              const Row(children: [Icon(Icons.schedule_rounded, size: 15), SizedBox(width: 5), Text('Estimated scan delivery: Sep 12', style: TextStyle(fontSize: 11))]),
            ],
          ),
        ),
      ),
    );
  }
}

class _FilmLabCard extends StatelessWidget {
  const _FilmLabCard({required this.lab, required this.onTap});
  final FilmLab lab;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(width: 94, child: FilmAssetImage(height: 98, alignment: -0.25)),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(lab.name, maxLines: 1, overflow: TextOverflow.ellipsis, style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 4),
                    Text('${lab.location} · ${lab.distance}', maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, color: Color(0xFF6B7571))),
                    const SizedBox(height: 8),
                    Wrap(spacing: 5, runSpacing: 5, children: lab.formats.take(3).map((format) => Container(padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3), decoration: BoxDecoration(color: const Color(0xFFF0F3F1), borderRadius: BorderRadius.circular(4)), child: Text(format, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w700)))).toList()),
                    const SizedBox(height: 9),
                    Row(children: [const Icon(Icons.star_rounded, color: Color(0xFFD58A32), size: 16), Text(' ${lab.rating}', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800)), const Spacer(), Text('from ${formatVnd(lab.price)}', style: const TextStyle(fontSize: 10, color: AppTheme.teal, fontWeight: FontWeight.w800))]),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _QuickAction extends StatelessWidget {
  const _QuickAction({required this.icon, required this.label, required this.color, required this.onTap});
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton.icon(onPressed: onTap, icon: Icon(icon, color: color), label: Text(label), style: OutlinedButton.styleFrom(minimumSize: const Size(0, 54)));
  }
}

class _LabDetails extends StatefulWidget {
  const _LabDetails({required this.lab});
  final FilmLab lab;

  @override
  State<_LabDetails> createState() => _LabDetailsState();
}

class _LabDetailsState extends State<_LabDetails> {
  String _service = 'Develop + JPEG Scan';
  int _rolls = 1;

  @override
  Widget build(BuildContext context) {
    final total = widget.lab.price * _rolls;
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(18, 0, 18, 22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const FilmAssetImage(height: 180, alignment: -0.1),
            const SizedBox(height: 16),
            Text(widget.lab.name, style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 5),
            Text('${widget.lab.location} · ${widget.lab.turnaround}'),
            const SizedBox(height: 20),
            DropdownButtonFormField<String>(
              initialValue: _service,
              decoration: const InputDecoration(labelText: 'Processing service'),
              items: const ['Develop only', 'Develop + JPEG Scan', 'Develop + TIFF Scan'].map((value) => DropdownMenuItem(value: value, child: Text(value))).toList(),
              onChanged: (value) => setState(() => _service = value ?? _service),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                const Expanded(child: Text('Number of rolls', style: TextStyle(fontWeight: FontWeight.w700))),
                IconButton.outlined(onPressed: _rolls > 1 ? () => setState(() => _rolls--) : null, icon: const Icon(Icons.remove_rounded)),
                SizedBox(width: 38, child: Text('$_rolls', textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.w800))),
                IconButton.filled(onPressed: () => setState(() => _rolls++), icon: const Icon(Icons.add_rounded)),
              ],
            ),
            const Divider(height: 28),
            Row(children: [const Text('Estimated total'), const Spacer(), Text(formatVnd(total), style: const TextStyle(fontSize: 16, color: AppTheme.teal, fontWeight: FontWeight.w900))]),
            const SizedBox(height: 16),
            SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () => _confirmBooking(context), icon: const Icon(Icons.calendar_month_rounded), label: const Text('Book service'))),
          ],
        ),
      ),
    );
  }

  void _confirmBooking(BuildContext context) {
    Navigator.pop(context);
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Booking draft created for ${widget.lab.name}.')));
  }
}

class _OrderPreview extends StatelessWidget {
  const _OrderPreview();

  @override
  Widget build(BuildContext context) {
    return const SafeArea(
      child: Padding(
        padding: EdgeInsets.fromLTRB(20, 0, 20, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('FL-2048', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900)),
            SizedBox(height: 4),
            Text('The film is currently being developed. The Film Lab will notify you before scanning starts.'),
            SizedBox(height: 18),
            LinearProgressIndicator(value: 0.48, minHeight: 6, borderRadius: BorderRadius.all(Radius.circular(3))),
          ],
        ),
      ),
    );
  }
}

class _NoResults extends StatelessWidget {
  const _NoResults();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.symmetric(vertical: 28),
      child: Column(children: [Icon(Icons.search_off_rounded, size: 34, color: Color(0xFF88928E)), SizedBox(height: 9), Text('No Film Labs match these filters', style: TextStyle(fontWeight: FontWeight.w800)), SizedBox(height: 4), Text('Try another format or search a nearby district.')]),
    );
  }
}

class _AssistantSheet extends StatefulWidget {
  const _AssistantSheet();

  @override
  State<_AssistantSheet> createState() => _AssistantSheetState();
}

class _AssistantSheetState extends State<_AssistantSheet> {
  final _controller = TextEditingController();
  String? _answer;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.fromLTRB(18, 0, 18, MediaQuery.viewInsetsOf(context).bottom + 18),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('AI Photography Assistant', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          const Text('Ask about film stock, exposure, scanning, or Film Lab services.'),
          const SizedBox(height: 14),
          TextField(
            controller: _controller,
            autofocus: true,
            minLines: 2,
            maxLines: 4,
            onChanged: (_) => setState(() {}),
            decoration: const InputDecoration(hintText: 'Which film stock works well for a cloudy afternoon?'),
          ),
          if (_answer != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: const Color(0xFFF0E7F5), borderRadius: BorderRadius.circular(7)),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.auto_awesome_rounded, size: 18, color: Color(0xFF76518E)),
                  const SizedBox(width: 9),
                  Expanded(child: Text(_answer!, style: const TextStyle(fontSize: 12))),
                ],
              ),
            ),
          ],
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: _controller.text.trim().isEmpty
                  ? null
                  : () {
                      FocusScope.of(context).unfocus();
                      setState(() => _answer = 'For soft cloudy light, ISO 400 color-negative film is a flexible starting point. Check the camera meter and expose for the shadows.');
                    },
              icon: const Icon(Icons.arrow_upward_rounded),
              label: const Text('Ask assistant'),
            ),
          ),
        ],
      ),
    );
  }
}
