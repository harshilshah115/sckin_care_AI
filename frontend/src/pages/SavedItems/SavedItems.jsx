import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Sidebar from '../../components/Sidebar/Sidebar'
import Loader from '../../components/Loader/Loader'
import { savedAPI } from '../../services/api'
import './SavedItems.css'

function SavedItems() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('products')
  const [loading, setLoading] = useState(true)
  const [savedProducts, setSavedProducts] = useState([])
  const [savedRoutines, setSavedRoutines] = useState([])
  const [savedRemedies, setSavedRemedies] = useState([])

  useEffect(() => {
    loadSavedItems()
  }, [])

  const loadSavedItems = async () => {
    setLoading(true)
    try {
      const items = await savedAPI.getSavedItems()
      
      // Separate by type
      setSavedProducts(items.filter(i => i.item_type === 'product'))
      setSavedRoutines(items.filter(i => i.item_type === 'routine'))
      setSavedRemedies(items.filter(i => i.item_type === 'remedy'))
    } catch (error) {
      console.error('Error loading saved items:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = async (itemId) => {
    try {
      await savedAPI.removeSavedItem(itemId)
      loadSavedItems() // Reload
    } catch (error) {
      console.error('Error removing item:', error)
    }
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
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
            <span className="material-symbols-outlined">bookmark</span>
            <h1>Saved Items</h1>
          </div>

          <div className="header-actions">
            <Link to="/products" className="btn btn-secondary">
              <span className="material-symbols-outlined">shopping_bag</span>
              Browse Products
            </Link>
          </div>
        </header>

        <div className="saved-content">
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
              <Loader />
            </div>
          ) : (
            <>
              <div className="saved-tabs">
                <button 
                  className={`tab-btn ${activeTab === 'products' ? 'active' : ''}`}
                  onClick={() => setActiveTab('products')}
                >
                  <span className="material-symbols-outlined">inventory_2</span>
                  Products
                  <span className="tab-count">{savedProducts.length}</span>
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'routines' ? 'active' : ''}`}
                  onClick={() => setActiveTab('routines')}
                >
                  <span className="material-symbols-outlined">event_note</span>
                  Routines
                  <span className="tab-count">{savedRoutines.length}</span>
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'remedies' ? 'active' : ''}`}
                  onClick={() => setActiveTab('remedies')}
                >
                  <span className="material-symbols-outlined">spa</span>
                  Remedies
                  <span className="tab-count">{savedRemedies.length}</span>
                </button>
              </div>

          {activeTab === 'products' && (
            <div className="saved-grid">
              {savedProducts.length > 0 ? (
                savedProducts.map((product) => (
                  <div key={product.id} className="saved-product-card">
                    <div className="product-image">
                      <img src={product.item_data?.image || product.image} alt={product.item_data?.name || product.name} />
                      {product.item_data?.match_score && (
                        <div className="match-badge">{product.item_data.match_score}% Match</div>
                      )}
                    </div>
                    <div className="product-info">
                      <span className="product-brand">{product.item_data?.brand || 'Brand'}</span>
                      <h3 className="product-name">{product.item_data?.name || product.name}</h3>
                      <div className="product-meta">
                        {product.item_data?.rating && (
                          <div className="product-rating">
                            <span className="material-symbols-outlined">star</span>
                            {product.item_data.rating}
                          </div>
                        )}
                        {product.item_data?.price && (
                          <span className="product-price">{product.item_data.price}</span>
                        )}
                      </div>
                      <span className="saved-date">Saved {formatDate(product.created_at)}</span>
                    </div>
                    <div className="card-actions">
                      <button className="btn btn-primary btn-sm">View Details</button>
                      <button className="btn-icon" onClick={() => handleRemove(product.id)}>
                        <span className="material-symbols-outlined">delete</span>
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '4rem' }}>
                  <span className="material-symbols-outlined" style={{ fontSize: '4rem', opacity: 0.3 }}>bookmark_border</span>
                  <h3>No saved products</h3>
                  <p>Products you save will appear here</p>
                  <Link to="/products" className="btn btn-primary">Browse Products</Link>
                </div>
              )}
            </div>
          )}

          {activeTab === 'routines' && (
            <div className="saved-list">
              {savedRoutines.length > 0 ? (
                savedRoutines.map((routine) => (
                  <div key={routine.id} className="saved-routine-card">
                    <div className="routine-icon">
                      <span className="material-symbols-outlined">event_note</span>
                    </div>
                    <div className="routine-info">
                      <h3>{routine.item_data?.name || routine.name}</h3>
                      <div className="routine-meta">
                        {routine.item_data?.steps && (
                          <span><span className="material-symbols-outlined">layers</span>{routine.item_data.steps} steps</span>
                        )}
                        {routine.item_data?.duration && (
                          <span><span className="material-symbols-outlined">timer</span>{routine.item_data.duration}</span>
                        )}
                      </div>
                      <span className="saved-date">Saved {formatDate(routine.created_at)}</span>
                    </div>
                    <div className="card-actions vertical">
                      <button className="btn btn-primary btn-sm">Start Routine</button>
                      <button className="btn-icon" onClick={() => handleRemove(routine.id)}>
                        <span className="material-symbols-outlined">delete</span>
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state" style={{ textAlign: 'center', padding: '4rem' }}>
                  <span className="material-symbols-outlined" style={{ fontSize: '4rem', opacity: 0.3 }}>event_note</span>
                  <h3>No saved routines</h3>
                  <p>Skincare routines you save will appear here</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'remedies' && (
            <div className="saved-list">
              {savedRemedies.length > 0 ? (
                savedRemedies.map((remedy) => (
                  <div key={remedy.id} className="saved-remedy-card">
                    <div className="remedy-icon">
                      <span className="material-symbols-outlined">spa</span>
                    </div>
                    <div className="remedy-info">
                      <h3>{remedy.item_data?.title || remedy.title}</h3>
                      <p className="remedy-description">{remedy.item_data?.description || remedy.description}</p>
                      {remedy.item_data?.ingredients && (
                        <div className="remedy-ingredients">
                          <span className="label">Ingredients:</span>
                          {remedy.item_data.ingredients.map((ing, i) => (
                            <span key={i} className="ingredient-tag">{ing}</span>
                          ))}
                        </div>
                      )}
                      <span className="saved-date">Saved {formatDate(remedy.created_at)}</span>
                    </div>
                    <div className="card-actions vertical">
                      <button className="btn btn-primary btn-sm">View Recipe</button>
                      <button className="btn-icon" onClick={() => handleRemove(remedy.id)}>
                        <span className="material-symbols-outlined">delete</span>
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state" style={{ textAlign: 'center', padding: '4rem' }}>
                  <span className="material-symbols-outlined" style={{ fontSize: '4rem', opacity: 0.3 }}>spa</span>
                  <h3>No saved remedies</h3>
                  <p>Natural remedies you save will appear here</p>
                </div>
              )}
            </div>
          )}
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default SavedItems
