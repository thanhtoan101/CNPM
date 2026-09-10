import 'package:flutter/material.dart';

import '../data/demo_data.dart';
import '../models/app_models.dart';
import '../theme/app_theme.dart';
import '../widgets/common_widgets.dart';

class MarketplaceScreen extends StatefulWidget {
  const MarketplaceScreen({super.key});

  @override
  State<MarketplaceScreen> createState() => _MarketplaceScreenState();
}

class _MarketplaceScreenState extends State<MarketplaceScreen> {
  String _category = 'All';

  @override
  Widget build(BuildContext context) {
    final filtered = marketplaceListings.where((item) => _category == 'All' || item.category == _category).toList();
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 24),
      children: [
        TextField(decoration: InputDecoration(hintText: 'Search cameras, lenses, or film', prefixIcon: const Icon(Icons.search_rounded), suffixIcon: IconButton(tooltip: 'Marketplace filters', onPressed: () {}, icon: const Icon(Icons.tune_rounded)))),
        const SizedBox(height: 12),
        SizedBox(height: 34, child: ListView(scrollDirection: Axis.horizontal, children: ['All', 'Camera', 'Lens', 'Film'].map((category) => Padding(padding: const EdgeInsets.only(right: 8), child: ChoiceChip(label: Text(category), selected: _category == category, onSelected: (_) => setState(() => _category = category), labelStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700), visualDensity: VisualDensity.compact))).toList())),
        const SizedBox(height: 18),
        Row(children: [Expanded(child: Text('Recent listings', style: Theme.of(context).textTheme.titleLarge)), FilledButton.icon(onPressed: () => _showCreateListing(context), icon: const Icon(Icons.add_rounded), label: const Text('Sell item'))]),
        const SizedBox(height: 12),
        ...filtered.map((listing) => Padding(padding: const EdgeInsets.only(bottom: 11), child: _ListingCard(listing: listing))),
      ],
    );
  }

  void _showCreateListing(BuildContext context) {
    showModalBottomSheet<void>(context: context, isScrollControlled: true, showDragHandle: true, builder: (context) => Padding(padding: EdgeInsets.fromLTRB(18, 0, 18, MediaQuery.viewInsetsOf(context).bottom + 20), child: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [Text('Create listing', style: Theme.of(context).textTheme.titleLarge), const SizedBox(height: 14), const TextField(decoration: InputDecoration(labelText: 'Item title')), const SizedBox(height: 10), const TextField(keyboardType: TextInputType.number, decoration: InputDecoration(labelText: 'Price in VND')), const SizedBox(height: 10), const TextField(maxLines: 3, decoration: InputDecoration(labelText: 'Condition and description')), const SizedBox(height: 14), SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () { Navigator.pop(context); ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Listing saved as a draft.'))); }, icon: const Icon(Icons.save_outlined), label: const Text('Save draft')))]))));
  }
}

class _ListingCard extends StatelessWidget {
  const _ListingCard({required this.listing});
  final MarketplaceListing listing;

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => _showDetails(context),
        child: Row(
          children: [
            SizedBox(width: 118, height: 132, child: FilmAssetImage(alignment: listing.alignment, borderRadius: BorderRadius.zero)),
            Expanded(child: Padding(padding: const EdgeInsets.all(12), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Row(children: [Expanded(child: Text(listing.category.toUpperCase(), style: const TextStyle(color: Color(0xFF78837E), fontSize: 9, fontWeight: FontWeight.w800))), _MarketStatus(status: listing.status)]), const SizedBox(height: 7), Text(listing.title, maxLines: 2, overflow: TextOverflow.ellipsis, style: Theme.of(context).textTheme.titleMedium), const SizedBox(height: 7), Text(formatVnd(listing.price), style: const TextStyle(color: AppTheme.teal, fontSize: 13, fontWeight: FontWeight.w900)), const SizedBox(height: 8), Row(children: [const Icon(Icons.location_on_outlined, size: 14), const SizedBox(width: 3), Expanded(child: Text(listing.location, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 10)))])]))),
          ],
        ),
      ),
    );
  }

  void _showDetails(BuildContext context) {
    showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (context) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(18, 0, 18, 20), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [FilmAssetImage(height: 190, alignment: listing.alignment), const SizedBox(height: 14), Text(listing.title, style: Theme.of(context).textTheme.titleLarge), Text(formatVnd(listing.price), style: const TextStyle(color: AppTheme.teal, fontSize: 16, fontWeight: FontWeight.w900)), const SizedBox(height: 6), Text('${listing.status} · ${listing.location}'), const SizedBox(height: 15), SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () { Navigator.pop(context); ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Conversation opened for ${listing.title}.'))); }, icon: const Icon(Icons.chat_bubble_outline_rounded), label: const Text('Contact seller')))]))));
  }
}

class _MarketStatus extends StatelessWidget {
  const _MarketStatus({required this.status});
  final String status;

  @override
  Widget build(BuildContext context) {
    final available = status == 'Available';
    return Container(padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 4), decoration: BoxDecoration(color: available ? const Color(0xFFE5F1E7) : const Color(0xFFFBEFD4), borderRadius: BorderRadius.circular(20)), child: Text(status, style: TextStyle(color: available ? const Color(0xFF347046) : const Color(0xFF92600C), fontSize: 9, fontWeight: FontWeight.w800)));
  }
}
