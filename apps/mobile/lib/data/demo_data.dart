import '../models/app_models.dart';

const filmLabs = [
  FilmLab(
    name: 'Saigon Grain Lab',
    location: 'District 3, Ho Chi Minh City',
    distance: '1.8 km',
    rating: 4.9,
    price: 155000,
    turnaround: '2-3 days',
    formats: ['35mm', '120', 'C-41'],
  ),
  FilmLab(
    name: 'Retrocam Film Lab',
    location: 'District 1, Ho Chi Minh City',
    distance: '3.4 km',
    rating: 4.7,
    price: 145000,
    turnaround: '3 days',
    formats: ['35mm', 'B&W', 'ECN-2'],
  ),
  FilmLab(
    name: 'The Darkroom Studio',
    location: 'Binh Thanh, Ho Chi Minh City',
    distance: '5.1 km',
    rating: 4.8,
    price: 175000,
    turnaround: '2 days',
    formats: ['35mm', '120', 'B&W'],
  ),
];

const filmOrders = [
  FilmOrder(
    id: 'FL-2048',
    lab: 'Saigon Grain Lab',
    service: 'Develop + Scan XL',
    status: OrderStatus.processing,
    updatedAt: 'Today, 14:20',
    rolls: 2,
  ),
  FilmOrder(
    id: 'FL-2028',
    lab: 'Retrocam Film Lab',
    service: 'Develop + JPEG Scan',
    status: OrderStatus.ready,
    updatedAt: 'Yesterday, 18:40',
    rolls: 1,
  ),
  FilmOrder(
    id: 'FL-1996',
    lab: 'The Darkroom Studio',
    service: 'B&W Develop + Scan',
    status: OrderStatus.completed,
    updatedAt: 'September 4, 11:15',
    rolls: 2,
  ),
];

const archiveAlbums = [
  ArchiveAlbum(title: 'Da Lat morning', subtitle: 'Portra 400', count: 24, alignment: -0.8),
  ArchiveAlbum(title: 'Saigon after rain', subtitle: 'Cinestill 800T', count: 18, alignment: 0.9),
  ArchiveAlbum(title: 'Coastal walk', subtitle: 'Gold 200', count: 32, alignment: -0.2),
  ArchiveAlbum(title: 'Weekend photowalk', subtitle: 'Ultramax 400', count: 21, alignment: 0.5),
];

const marketplaceListings = [
  MarketplaceListing(
    title: '35mm rangefinder body',
    category: 'Camera',
    price: 8900000,
    location: 'Ho Chi Minh City',
    status: 'Available',
    alignment: -0.45,
  ),
  MarketplaceListing(
    title: '50mm manual focus lens',
    category: 'Lens',
    price: 2450000,
    location: 'Da Nang',
    status: 'Reserved',
    alignment: 0.65,
  ),
  MarketplaceListing(
    title: 'Fresh color film bundle',
    category: 'Film',
    price: 520000,
    location: 'Ha Noi',
    status: 'Available',
    alignment: 0.1,
  ),
];

