import 'package:flutter/material.dart';

import '../models/app_models.dart';
import '../theme/app_theme.dart';

class SectionHeader extends StatelessWidget {
  const SectionHeader({
    required this.title,
    this.action,
    this.onAction,
    super.key,
  });

  final String title;
  final String? action;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: Text(title, style: Theme.of(context).textTheme.titleLarge)),
        if (action != null)
          TextButton(onPressed: onAction, child: Text(action!)),
      ],
    );
  }
}

class StatusChip extends StatelessWidget {
  const StatusChip({required this.status, super.key});

  final OrderStatus status;

  @override
  Widget build(BuildContext context) {
    final (foreground, background) = switch (status) {
      OrderStatus.pending || OrderStatus.pickupScheduled => (const Color(0xFF92600C), const Color(0xFFFBEFD4)),
      OrderStatus.received || OrderStatus.processing || OrderStatus.scanning => (AppTheme.teal, const Color(0xFFDFF2EE)),
      OrderStatus.ready || OrderStatus.completed => (const Color(0xFF347046), const Color(0xFFE5F1E7)),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
      decoration: BoxDecoration(color: background, borderRadius: BorderRadius.circular(20)),
      child: Text(
        status.label,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: TextStyle(color: foreground, fontSize: 10, fontWeight: FontWeight.w800),
      ),
    );
  }
}

class FilmAssetImage extends StatelessWidget {
  const FilmAssetImage({
    this.height,
    this.alignment = 0,
    this.borderRadius = const BorderRadius.all(Radius.circular(7)),
    super.key,
  });

  final double? height;
  final double alignment;
  final BorderRadius borderRadius;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: borderRadius,
      child: Image.asset(
        'assets/images/analog-workspace.png',
        width: double.infinity,
        height: height,
        fit: BoxFit.cover,
        alignment: Alignment(alignment, 0),
      ),
    );
  }
}

String formatVnd(int value) {
  final digits = value.toString();
  final buffer = StringBuffer();
  for (var index = 0; index < digits.length; index++) {
    if (index > 0 && (digits.length - index) % 3 == 0) buffer.write(',');
    buffer.write(digits[index]);
  }
  return '${buffer.toString()} VND';
}

