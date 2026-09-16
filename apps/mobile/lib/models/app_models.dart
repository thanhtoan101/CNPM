enum OrderStatus {
  pending('Pending'),
  pickupScheduled('Pickup scheduled'),
  received('Received by Film Lab'),
  processing('Processing'),
  scanning('Scanning'),
  ready('Ready for delivery'),
  completed('Completed');

  const OrderStatus(this.label);
  final String label;
}

class FilmLab {
  const FilmLab({
    required this.name,
    required this.location,
    required this.distance,
    required this.rating,
    required this.price,
    required this.turnaround,
    required this.formats,
  });

  final String name;
  final String location;
  final String distance;
  final double rating;
  final int price;
  final String turnaround;
  final List<String> formats;
}

class FilmOrder {
  const FilmOrder({
    required this.id,
    required this.lab,
    required this.service,
    required this.status,
    required this.updatedAt,
    required this.rolls,
  });

  final String id;
  final String lab;
  final String service;
  final OrderStatus status;
  final String updatedAt;
  final int rolls;
}

class ArchiveAlbum {
  const ArchiveAlbum({
    required this.title,
    required this.subtitle,
    required this.count,
    required this.alignment,
  });

  final String title;
  final String subtitle;
  final int count;
  final double alignment;
}

class MarketplaceListing {
  const MarketplaceListing({
    required this.title,
    required this.category,
    required this.price,
    required this.location,
    required this.status,
    required this.alignment,
  });

  final String title;
  final String category;
  final int price;
  final String location;
  final String status;
  final double alignment;
}

