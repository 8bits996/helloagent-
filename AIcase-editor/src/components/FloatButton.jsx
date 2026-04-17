import React from 'react'

function FloatButton({ onClick }) {
  return (
    <button 
      className="float-button"
      onClick={onClick}
      title="打开编辑器"
    >
      <span className="material-icons">edit</span>
    </button>
  )
}

export default FloatButton
