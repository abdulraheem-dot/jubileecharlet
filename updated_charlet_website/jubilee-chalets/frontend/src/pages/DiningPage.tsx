import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { contentApi } from '@/services/api/content'
import { getImageUrl } from '@/utils'
import SectionReveal from '@/components/common/SectionReveal'
import { Skeleton } from '@/components/ui/Skeleton'
import { Leaf, Wheat } from 'lucide-react'

export default function DiningPage() {
  const [activeCategory, setActiveCategory] = useState<number | null>(null)

  const { data: categories } = useQuery({ queryKey: ['menu-categories'], queryFn: contentApi.getMenuCategories })
  const { data: items, isLoading } = useQuery({
    queryKey: ['menu-items', activeCategory],
    queryFn: () => contentApi.getMenuItems(activeCategory ?? undefined),
  })

  return (
    <div className="pt-18 min-h-screen bg-white">
      {/* Hero */}
      <section className="relative bg-brand-forest-green text-white py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <img src="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=60" alt="" className="w-full h-full object-cover" />
        </div>
        <div className="relative z-10 container-xl text-center">
          <span className="text-green-300 text-sm font-semibold uppercase tracking-widest block mb-3">Dining</span>
          <h1 className="font-display text-4xl sm:text-5xl font-bold mb-4">Restaurant & Dining</h1>
          <p className="text-white/75 text-lg max-w-2xl mx-auto">
            Enjoy freshly prepared meals in our on-site restaurant, featuring a selection of local and continental dishes.
          </p>
        </div>
      </section>

      {/* Menu */}
      <section className="section-padding">
        <div className="container-xl">
          {/* Category filter */}
          {categories && categories.length > 0 && (
            <div className="flex gap-2 overflow-x-auto pb-2 mb-8 scrollbar-hide">
              <button
                onClick={() => setActiveCategory(null)}
                className={`shrink-0 px-5 py-2 rounded-full text-sm font-medium transition-colors ${!activeCategory ? 'bg-brand-dark-green text-white' : 'bg-white border border-gray-200 text-gray-600 hover:border-brand-dark-green'}`}
              >
                All Items
              </button>
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setActiveCategory(cat.id)}
                  className={`shrink-0 px-5 py-2 rounded-full text-sm font-medium transition-colors ${activeCategory === cat.id ? 'bg-brand-dark-green text-white' : 'bg-white border border-gray-200 text-gray-600 hover:border-brand-dark-green'}`}
                >
                  {cat.name}
                </button>
              ))}
            </div>
          )}

          {isLoading ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="card">
                  <Skeleton className="h-48 w-full" />
                  <div className="p-4 space-y-2">
                    <Skeleton className="h-5 w-2/3" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : !items?.length ? (
            <div className="text-center py-20">
              <p className="text-gray-500">Menu details will be available soon.</p>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {items.map((item, i) => (
                <SectionReveal key={item.id} delay={i * 0.06}>
                  <article className={`card group overflow-hidden ${!item.is_available ? 'opacity-60' : ''}`}>
                    {item.image && (
                      <div className="relative overflow-hidden aspect-video">
                        <img
                          src={getImageUrl(item.image)}
                          alt={item.name}
                          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                          loading="lazy"
                        />
                        {!item.is_available && (
                          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                            <span className="bg-white text-brand-black px-3 py-1 rounded-full text-xs font-semibold">Unavailable</span>
                          </div>
                        )}
                      </div>
                    )}
                    <div className="p-4">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div>
                          <h3 className="font-display font-bold text-base text-brand-black">{item.name}</h3>
                          <span className="text-xs text-brand-dark-green">{item.category.name}</span>
                        </div>
                        <span className="font-display font-bold text-base text-brand-dark-green shrink-0">
                          ₦{parseFloat(item.price).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm leading-relaxed mb-3 line-clamp-2">{item.description}</p>
                      <div className="flex items-center gap-2 flex-wrap">
                        {item.is_vegetarian && (
                          <span className="flex items-center gap-1 text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full">
                            <Leaf className="w-3 h-3" />Vegetarian
                          </span>
                        )}
                        {item.is_vegan && (
                          <span className="flex items-center gap-1 text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full">
                            <Leaf className="w-3 h-3" />Vegan
                          </span>
                        )}
                        {item.is_gluten_free && (
                          <span className="flex items-center gap-1 text-xs bg-amber-50 text-amber-700 px-2 py-0.5 rounded-full">
                            <Wheat className="w-3 h-3" />Gluten-free
                          </span>
                        )}
                      </div>
                    </div>
                  </article>
                </SectionReveal>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
