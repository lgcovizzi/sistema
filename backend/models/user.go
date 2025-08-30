package models

import (
	"time"

	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

// User representa um usuário do sistema
type User struct {
	ID           uuid.UUID `json:"id" gorm:"type:uuid;primary_key;default:gen_random_uuid()"`
	Name         string    `json:"name" gorm:"not null;size:255"`
	Email        string    `json:"email" gorm:"uniqueIndex;not null;size:255"`
	PasswordHash string    `json:"-" gorm:"column:password_hash;not null;size:255"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
	DeletedAt    gorm.DeletedAt `json:"-" gorm:"index"`
}

// BeforeCreate hook para gerar UUID antes de criar
func (u *User) BeforeCreate(tx *gorm.DB) error {
	if u.ID == uuid.Nil {
		u.ID = uuid.New()
	}
	return nil
}

// HashPassword criptografa a senha do usuário
func (u *User) HashPassword(password string) error {
	hashed, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}
	u.PasswordHash = string(hashed)
	return nil
}

// CheckPassword verifica se a senha está correta
func (u *User) CheckPassword(password string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(u.PasswordHash), []byte(password))
	return err == nil
}

// TableName especifica o nome da tabela
func (User) TableName() string {
	return "users"
}