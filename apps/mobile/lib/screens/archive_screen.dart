import 'package:flutter/material.dart';

import '../data/demo_data.dart';
import '../models/app_models.dart';
import '../widgets/common_widgets.dart';

class ArchiveScreen extends StatefulWidget {
  const ArchiveScreen({super.key});

  @override
  State<ArchiveScreen> createState() => _ArchiveScreenState();
}

class _ArchiveScreenState extends State<ArchiveScreen> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final albums = archiveAlbums.where((album) => '${album.title} ${album.subtitle}'.toLowerCase().contains(_searchController.text.toLowerCase())).toList();
    return CustomScrollView(
      slivers: [
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(16, 14, 16, 12),
          sliver: SliverList.list(children: [
            TextField(controller: _searchController, onChanged: (_) => setState(() {}), decoration: const InputDecoration(hintText: 'Search albums, film stock, or tags', prefixIcon: Icon(Icons.search_rounded), suffixIcon: Icon(Icons.filter_list_rounded))),
            const SizedBox(height: 16),
            Row(children: [Expanded(child: _ArchiveMetric(label: 'Photos', value: '286', icon: Icons.photo_outlined)), const SizedBox(width: 9), Expanded(child: _ArchiveMetric(label: 'Albums', value: '12', icon: Icons.photo_album_outlined)), const SizedBox(width: 9), Expanded(child: _ArchiveMetric(label: 'Private', value: '100%', icon: Icons.lock_outline_rounded))]),
            const SizedBox(height: 20),
            SectionHeader(title: 'Your albums', action: 'New album', onAction: () => _showNewAlbum(context)),
          ]),
        ),
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
          sliver: SliverGrid(
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 2, childAspectRatio: 0.79, crossAxisSpacing: 10, mainAxisSpacing: 10),
            delegate: SliverChildBuilderDelegate((context, index) => _AlbumCard(album: albums[index]), childCount: albums.length),
          ),
        ),
      ],
    );
  }

  void _showNewAlbum(BuildContext context) {
    showDialog<void>(context: context, builder: (context) => AlertDialog(title: const Text('Create album'), content: const TextField(decoration: InputDecoration(labelText: 'Album name')), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')), FilledButton(onPressed: () { Navigator.pop(context); ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('New album created.'))); }, child: const Text('Create'))]));
  }
}

class _ArchiveMetric extends StatelessWidget {
  const _ArchiveMetric({required this.label, required this.value, required this.icon});
  final String label;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(padding: const EdgeInsets.all(10), decoration: BoxDecoration(color: Colors.white, border: Border.all(color: const Color(0xFFDCE2DE)), borderRadius: BorderRadius.circular(7)), child: Column(children: [Icon(icon, size: 19, color: Theme.of(context).colorScheme.primary), const SizedBox(height: 5), Text(value, style: const TextStyle(fontWeight: FontWeight.w900)), Text(label, style: const TextStyle(fontSize: 9, color: Color(0xFF73807A)))]));
  }
}

class _AlbumCard extends StatelessWidget {
  const _AlbumCard({required this.album});
  final ArchiveAlbum album;

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => _showAlbum(context),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(child: FilmAssetImage(alignment: album.alignment, borderRadius: BorderRadius.zero)),
            Padding(padding: const EdgeInsets.all(10), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(album.title, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800)), const SizedBox(height: 3), Text('${album.subtitle} · ${album.count} scans', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 9, color: Color(0xFF73807A)))])),
          ],
        ),
      ),
    );
  }

  void _showAlbum(BuildContext context) {
    showModalBottomSheet<void>(context: context, showDragHandle: true, builder: (context) => SafeArea(child: Padding(padding: const EdgeInsets.fromLTRB(18, 0, 18, 24), child: Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [FilmAssetImage(height: 210, alignment: album.alignment), const SizedBox(height: 14), Text(album.title, style: Theme.of(context).textTheme.titleLarge), Text('${album.subtitle} · ${album.count} private scans'), const SizedBox(height: 15), Row(children: [Expanded(child: OutlinedButton.icon(onPressed: () => _notify(context, 'Album download started.'), icon: const Icon(Icons.download_rounded), label: const Text('Download'))), const SizedBox(width: 8), Expanded(child: FilledButton.icon(onPressed: () => _notify(context, '${album.title} opened.'), icon: const Icon(Icons.photo_library_outlined), label: const Text('Open album')))] )]))));
  }

  void _notify(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }
}
