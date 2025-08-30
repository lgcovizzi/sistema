package models

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// Product representa um produto do sistema
type Product struct {
	ID          uuid.UUID `json:"id" gorm:"type:uuid;primary_key;default:gen_random_uuid()"`
	Name        string    `json:"name" gorm:"not null;size:255"`
	Description string    `json:"description" gorm:"type:text"`
	Price       float64   `json:"price" gorm:"not null;type:decimal(10,2)"`
	Stock       int       `json:"stock" gorm:"not null;default:0"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
	DeletedAt   gorm.DeletedAt `json:"-" gorm:"index"`
}

// BeforeCreate hook para gerar UUID antes de criar
func (p *Product) BeforeCreate(tx *gorm.DB) error {
	if p.ID == uuid.Nil {
		p.ID = uuid.New()
	}
	return nil
}

// TableName especifica o nome da tabela
func (Product) TableName() string {
	return "products"
}