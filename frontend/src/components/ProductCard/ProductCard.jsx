import { Link } from 'react-router-dom'
import './ProductCard.css'

function ProductCard({ product, isSaved, onToggleSave }) {
  if (!product) return null

  return (
    <div className="product-card">
      <div className="product-image">
        <img src={product.image} alt={product.name} loading="lazy" />
        {product.matchScore && (
          <div className="match-badge">
            <span className="material-symbols-outlined">verified</span>
            {product.matchScore}% Match
          </div>
        )}
        {onToggleSave && (
          <button
            className={`save-btn ${isSaved ? 'saved' : ''}`}
            onClick={() => onToggleSave(product.id)}
            aria-label={isSaved ? 'Unsave product' : 'Save product'}
          >
            <span className="material-symbols-outlined">
              {isSaved ? 'bookmark' : 'bookmark_border'}
            </span>
          </button>
        )}
      </div>

      <div className="product-info">
        <span className="product-brand">{product.brand}</span>
        <h3 className="product-name">{product.name}</h3>

        {product.rating && (
          <div className="product-rating">
            <span className="material-symbols-outlined">star</span>
            <span className="rating-value">{product.rating}</span>
            {product.reviews && (
              <span className="review-count">({product.reviews.toLocaleString()})</span>
            )}
          </div>
        )}

        {product.skinTypes && (
          <div className="product-tags">
            {product.skinTypes.map((type, index) => (
              <span key={index} className="tag">{type}</span>
            ))}
          </div>
        )}

        {product.keyIngredients && (
          <div className="product-ingredients">
            <span className="ingredients-label">Key Ingredients: </span>
            <span className="ingredients-list">{product.keyIngredients.join(', ')}</span>
          </div>
        )}
      </div>

      <div className="product-footer">
        {product.price && <span className="product-price">{product.price}</span>}
        <Link to={`/products/${product.id}`} className="btn btn-primary btn-sm">View Details</Link>
      </div>
    </div>
  )
}

export default ProductCard