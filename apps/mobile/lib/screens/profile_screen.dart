import 'package:flutter/material.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _orderUpdates = true;
  bool _marketplaceUpdates = false;
  bool _privateArchive = true;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 24),
      children: [
        Card(child: Padding(padding: const EdgeInsets.all(16), child: Row(children: [CircleAvatar(radius: 27, backgroundColor: const Color(0xFFDFF2EE), child: Text('KD', style: TextStyle(color: Theme.of(context).colorScheme.primary, fontWeight: FontWeight.w900))), const SizedBox(width: 13), const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('Nguyen Dao Quoc Khanh', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w900)), SizedBox(height: 3), Text('Photographer · Ho Chi Minh City', style: TextStyle(fontSize: 11))])), IconButton(tooltip: 'Edit profile', onPressed: () {}, icon: const Icon(Icons.edit_outlined))]))),
        const SizedBox(height: 20),
        Text('Account', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        const _ProfileTile(icon: Icons.person_outline_rounded, title: 'Personal information'),
        const _ProfileTile(icon: Icons.location_on_outlined, title: 'Saved addresses'),
        const _ProfileTile(icon: Icons.lock_outline_rounded, title: 'Password and security'),
        const SizedBox(height: 20),
        Text('Preferences', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        Card(child: Column(children: [SwitchListTile(title: const Text('Order updates'), subtitle: const Text('Status and scan delivery notifications'), value: _orderUpdates, onChanged: (value) => setState(() => _orderUpdates = value)), const Divider(height: 1), SwitchListTile(title: const Text('Marketplace updates'), subtitle: const Text('Saved items and messages'), value: _marketplaceUpdates, onChanged: (value) => setState(() => _marketplaceUpdates = value)), const Divider(height: 1), SwitchListTile(title: const Text('Private archive by default'), subtitle: const Text('New scan deliveries remain private'), value: _privateArchive, onChanged: (value) => setState(() => _privateArchive = value))])),
        const SizedBox(height: 18),
        OutlinedButton.icon(onPressed: () => _confirmSignOut(context), icon: const Icon(Icons.logout_rounded), label: const Text('Sign out')),
      ],
    );
  }

  void _confirmSignOut(BuildContext context) {
    showDialog<void>(context: context, builder: (context) => AlertDialog(title: const Text('Sign out?'), content: const Text('You will need to sign in again to access orders and private scans.'), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context), child: const Text('Sign out'))]));
  }
}

class _ProfileTile extends StatelessWidget {
  const _ProfileTile({required this.icon, required this.title});
  final IconData icon;
  final String title;

  @override
  Widget build(BuildContext context) {
    return Card(margin: const EdgeInsets.only(bottom: 8), child: ListTile(leading: Icon(icon), title: Text(title, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700)), trailing: const Icon(Icons.chevron_right_rounded), onTap: () {}));
  }
}

