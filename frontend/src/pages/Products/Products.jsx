import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Sidebar from '../../components/Sidebar/Sidebar'
import { savedAPI } from '../../services/api'
import './Products.css'

function Products() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activeCategory, setActiveCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState('recommended')
  const [savedProductIds, setSavedProductIds] = useState([])

  useEffect(() => {
    loadSavedProducts()
  }, [])

  const loadSavedProducts = async () => {
    try {
      const items = await savedAPI.getSavedItems()
      const productIds = items
        .filter(i => i.item_type === 'product')
        .map(i => i.item_id)
      setSavedProductIds(productIds)
    } catch (error) {
      console.error('Error loading saved products:', error)
    }
  }

  const categories = [
    { id: 'all', label: 'All Products', icon: 'grid_view' },
    { id: 'cleanser', label: 'Cleansers', icon: 'water_drop' },
    { id: 'moisturizer', label: 'Moisturizers', icon: 'humidity_percentage' },
    { id: 'sunscreen', label: 'Sunscreens', icon: 'wb_sunny' },
    { id: 'serum', label: 'Serums', icon: 'science' },
    { id: 'toner', label: 'Toners', icon: 'auto_fix_high' },
  ]

  const products = [
    {
      id: 1,
      name: 'Gentle Foaming Cleanser',
      brand: 'CeraVe',
      category: 'cleanser',
      price: '₹799',
      rating: 4.7,
      reviews: 2453,
      skinTypes: ['Oily', 'Combination'],
      keyIngredients: ['Niacinamide', 'Ceramides', 'Hyaluronic Acid'],
      image: 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=300&h=300&fit=crop',
      matchScore: 95,
    },
    {
      id: 2,
      name: 'Daily Moisturizing Lotion',
      brand: 'Cetaphil',
      category: 'moisturizer',
      price: '₹650',
      rating: 4.5,
      reviews: 1876,
      skinTypes: ['All Skin Types'],
      keyIngredients: ['Vitamin E', 'Glycerin'],
      image: 'https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=300&h=300&fit=crop',
      matchScore: 88,
    },
    {
      id: 3,
      name: 'UV Expert Sunscreen SPF 50+',
      brand: "L'Oreal",
      category: 'sunscreen',
      price: '₹999',
      rating: 4.6,
      reviews: 892,
      skinTypes: ['All Skin Types'],
      keyIngredients: ['Vitamin E', 'Mexoryl'],
      image: 'https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=300&h=300&fit=crop',
      matchScore: 92,
    },
    {
      id: 4,
      name: 'Niacinamide 10% + Zinc 1%',
      brand: 'The Ordinary',
      category: 'serum',
      price: '₹590',
      rating: 4.8,
      reviews: 5432,
      skinTypes: ['Oily', 'Acne-Prone'],
      keyIngredients: ['Niacinamide', 'Zinc'],
      image: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=300&h=300&fit=crop',
      matchScore: 97,
    },
    {
      id: 5,
      name: 'Salicylic Acid Cleanser',
      brand: 'Paula\'s Choice',
      category: 'cleanser',
      price: '₹1299',
      rating: 4.4,
      reviews: 1234,
      skinTypes: ['Oily', 'Acne-Prone'],
      keyIngredients: ['Salicylic Acid 2%'],
      image: 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=300&h=300&fit=crop',
      matchScore: 85,
    },
    {
      id: 6,
      name: 'Hydrating Toner',
      brand: 'Klairs',
      category: 'toner',
      price: '₹1450',
      rating: 4.6,
      reviews: 987,
      skinTypes: ['Dry', 'Sensitive'],
      keyIngredients: ['Hyaluronic Acid', 'Centella'],
      image: 'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=300&h=300&fit=crop',
      matchScore: 78,
    },
  ]

  const filteredProducts = products
    .filter(p => activeCategory === 'all' || p.category === activeCategory)
    .filter(p => p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                 p.brand.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => {
      if (sortBy === 'recommended') return b.matchScore - a.matchScore
      if (sortBy === 'rating') return b.rating - a.rating
      if (sortBy === 'price-low') return parseInt(a.price.replace(/\D/g, '')) - parseInt(b.price.replace(/\D/g, ''))
      if (sortBy === 'price-high') return parseInt(b.price.replace(/\D/g, '')) - parseInt(a.price.replace(/\D/g, ''))
      return 0
    })

  const toggleSave = async (productId) => {
    const isSaved = savedProductIds.includes(productId)
    
    try {
      if (isSaved) {
        // Find the saved item ID and remove it
        const items = await savedAPI.getSavedItems()
        const savedItem = items.find(i => i.item_type === 'product' && i.item_id === productId)
        if (savedItem) {
          await savedAPI.removeSavedItem(savedItem.id)
          setSavedProductIds(prev => prev.filter(id => id !== productId))
        }
      } else {
        // Save the product
        const product = products.find(p => p.id === productId)
        if (product) {
          await savedAPI.saveItem({
            item_type: 'product',
            item_id: productId,
            item_data: product
          })
          setSavedProductIds(prev => [...prev, productId])
        }
      }
    } catch (error) {
      console.error('Error toggling save:', error)
    }
  }

  return (
    <div className="dashboard-layout">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="dashboard-main">
        <header className="dashboard-header">
          <button className="mobile-menu-toggle" onClick={() => setSidebarOpen(true)}>
            <span className="material-symbols-outlined">menu</span>
          </button>

          <div className="page-title">
            <span className="material-symbols-outlined">shopping_bag</span>
            <h1>Product Recommendations</h1>
          </div>

          <div className="header-actions">
            <Link to="/saved" className="btn btn-secondary">
              <span className="material-symbols-outlined">bookmark</span>
              Saved Items
            </Link>
          </div>
        </header>

        <div className="products-content">
          <div className="products-toolbar">
            <div className="search-box">
              <span className="material-symbols-outlined">search</span>
              <input 
                type="text"
                placeholder="Search products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <select 
              className="sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="recommended">Best Match</option>
              <option value="rating">Highest Rated</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
            </select>
          </div>

          <div className="category-tabs">
            {categories.map((cat) => (
              <button 
                key={cat.id}
                className={`category-tab ${activeCategory === cat.id ? 'active' : ''}`}
                onClick={() => setActiveCategory(cat.id)}
              >
                <span className="material-symbols-outlined">{cat.icon}</span>
                <span>{cat.label}</span>
              </button>
            ))}
          </div>

          <div className="products-grid">
            {filteredProducts.map((product) => (
              <div key={product.id} className="product-card">
                <div className="product-image">
                  <img src={product.image} alt={product.name} />
                  <div className="match-badge">
                    <span className="material-symbols-outlined">verified</span>
                    {product.matchScore}% Match
                  </div>
                  <button 
                    className={`save-btn ${savedProductIds.includes(product.id) ? 'saved' : ''}`}
                    onClick={() => toggleSave(product.id)}
                  >
                    <span className="material-symbols-outlined">
                      {savedProductIds.includes(product.id) ? 'bookmark' : 'bookmark_border'}
                    </span>
                  </button>
                </div>
                
                <div className="product-info">
                  <span className="product-brand">{product.brand}</span>
                  <h3 className="product-name">{product.name}</h3>
                  
                  <div className="product-rating">
                    <span className="material-symbols-outlined">star</span>
                    <span className="rating-value">{product.rating}</span>
                    <span className="review-count">({product.reviews.toLocaleString()})</span>
                  </div>
                  
                  <div className="product-tags">
                    {product.skinTypes.map((type, index) => (
                      <span key={index} className="tag">{type}</span>
                    ))}
                  </div>
                  
                  <div className="product-ingredients">
                    <span className="ingredients-label">Key Ingredients: </span>
                    <span className="ingredients-list">{product.keyIngredients.join(', ')}</span>
                  </div>
                </div>
                
                <div className="product-footer">
                  <span className="product-price">{product.price}</span>
                  <button className="btn btn-primary btn-sm">View Details</button>
                </div>
              </div>
            ))}
          </div>

          {filteredProducts.length === 0 && (
            <div className="empty-state">
              <span className="material-symbols-outlined">inventory_2</span>
              <h3>No products found</h3>
              <p>Try adjusting your search or filter criteria</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default Products
