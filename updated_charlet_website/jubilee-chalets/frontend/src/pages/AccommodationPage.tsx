import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { SlidersHorizontal, LayoutGrid, List, Search, X } from 'lucide-react'
import { roomsApi } from '@/services/api/rooms'
import RoomCard from '@/features/accommodation/RoomCard'
import { RoomCardSkeleton } from '@/components/ui/Skeleton'
import SectionReveal from '@/components/common/SectionReveal'
import BookingSearchBar from '@/components/common/BookingSearchBar'

export default function AccommodationPage() {
  const [searchParams] = useSearchParams()
  const [layout, setLayout] = useState<'grid' | 'list'>('grid')
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState({
    check_in: searchParams.get('check_in') ?? '',
    check_out: searchParams.get('check_out') ?? '',
    num_adults: Number(searchParams.get('num_adults') ?? 1),
    num_children: Number(searchParams.get('num_children') ?? 0),
    category: '',
    min_price: '',
    max_price: '',
    ordering: '',
  })

  const { data: categories } = useQuery({
    queryKey: ['room-categories'],
    queryFn: roomsApi.getCategories,
  })

  const queryParams = {
    ...(filters.check_in && { check_in: filters.check_in }),
    ...(filters.check_out && { check_out: filters.check_out }),
    ...(filters.num_adults > 0 && { num_adults: filters.num_adults }),
    ...(filters.category && { category: filters.category }),
    ...(filters.min_price && { min_price: Number(filters.min_price) }),
    ...(filters.max_price && { max_price: Number(filters.max_price) }),
    ...(filters.ordering && { ordering: filters.ordering }),
  }

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['rooms', queryParams],
    queryFn: () => roomsApi.getRooms(queryParams),
  })

  const clearFilters = () => {
    setFilters({ check_in: '', check_out: '', num_adults: 1, num_children: 0, category: '', min_price: '', max_price: '', ordering: '' })
  }

  const hasFilters = !!(filters.category || filters.min_price || filters.max_price)

  return (
    <div className="pt-18 min-h-screen bg-brand-light-grey">
      {/* Hero */}
      <section className="bg-brand-forest-green text-white py-16 px-4 sm:px-6 lg:px-8">
        <div className="container-xl text-center">
          <span className="text-green-300 text-sm font-semibold uppercase tracking-widest block mb-3">Our Accommodation</span>
          <h1 className="font-display text-4xl sm:text-5xl font-bold mb-4">Rooms & Chalets</h1>
          <p className="text-white/75 text-lg max-w-2xl mx-auto">
            Choose from our selection of well-appointed rooms and chalets, each designed with your comfort in mind.
          </p>
        </div>
      </section>

      {/* Search bar */}
      <div className="container-xl px-4 sm:px-6 lg:px-8 -mt-6 relative z-10">
        <BookingSearchBar />
      </div>

      <div className="container-xl px-4 sm:px-6 lg:px-8 py-10">
        {/* Toolbar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <div>
            <p className="text-gray-700 text-sm">
              {isLoading ? 'Searching…' : `${data?.count ?? 0} accommodation${(data?.count ?? 0) !== 1 ? 's' : ''} found`}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {hasFilters && (
              <button onClick={clearFilters} className="flex items-center gap-1.5 text-sm text-red-600 hover:text-red-700 transition-colors">
                <X className="w-4 h-4" />
                Clear filters
              </button>
            )}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-colors ${showFilters ? 'bg-brand-dark-green text-white border-brand-dark-green' : 'bg-white text-gray-700 border-gray-200 hover:border-brand-dark-green'}`}
            >
              <SlidersHorizontal className="w-4 h-4" />
              Filters
            </button>
            <select
              value={filters.ordering}
              onChange={(e) => setFilters({ ...filters, ordering: e.target.value })}
              className="bg-white border border-gray-200 text-sm rounded-xl px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-brand-dark-green"
              aria-label="Sort rooms"
            >
              <option value="">Sort by</option>
              <option value="price_per_night">Price: Low to High</option>
              <option value="-price_per_night">Price: High to Low</option>
              <option value="-max_occupancy">Capacity: High to Low</option>
            </select>
            <div className="flex rounded-xl border border-gray-200 overflow-hidden">
              <button
                onClick={() => setLayout('grid')}
                className={`p-2 transition-colors ${layout === 'grid' ? 'bg-brand-dark-green text-white' : 'bg-white text-gray-500 hover:text-brand-dark-green'}`}
                aria-label="Grid layout" aria-pressed={layout === 'grid'}
              >
                <LayoutGrid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setLayout('list')}
                className={`p-2 transition-colors ${layout === 'list' ? 'bg-brand-dark-green text-white' : 'bg-white text-gray-500 hover:text-brand-dark-green'}`}
                aria-label="List layout" aria-pressed={layout === 'list'}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Filters panel */}
        {showFilters && (
          <div className="bg-white rounded-2xl border border-gray-100 p-5 mb-6 grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">Category</label>
              <select
                value={filters.category}
                onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                className="input-field text-sm"
                aria-label="Filter by category"
              >
                <option value="">All categories</option>
                {categories?.map((c) => (
                  <option key={c.id} value={c.slug}>{c.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">Min Price (₦)</label>
              <input
                type="number"
                value={filters.min_price}
                onChange={(e) => setFilters({ ...filters, min_price: e.target.value })}
                placeholder="No minimum"
                className="input-field text-sm"
                min={0}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">Max Price (₦)</label>
              <input
                type="number"
                value={filters.max_price}
                onChange={(e) => setFilters({ ...filters, max_price: e.target.value })}
                placeholder="No maximum"
                className="input-field text-sm"
                min={0}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">Min Occupancy</label>
              <input
                type="number"
                value={filters.num_adults}
                onChange={(e) => setFilters({ ...filters, num_adults: Number(e.target.value) })}
                min={1} max={20}
                className="input-field text-sm"
              />
            </div>
          </div>
        )}

        {/* Results */}
        {isLoading || isFetching ? (
          <div className={layout === 'grid' ? 'grid sm:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
            {Array.from({ length: 6 }).map((_, i) => <RoomCardSkeleton key={i} />)}
          </div>
        ) : !data?.results.length ? (
          <div className="text-center py-24">
            <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="font-display font-bold text-xl text-gray-600 mb-2">No rooms found</h3>
            <p className="text-gray-500 mb-6">Try adjusting your dates or filters.</p>
            <button onClick={clearFilters} className="btn-primary">Clear All Filters</button>
          </div>
        ) : (
          <div className={layout === 'grid' ? 'grid sm:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
            {data.results.map((room) => (
              <SectionReveal key={room.id}>
                <RoomCard room={room} compact={layout === 'list'} />
              </SectionReveal>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
