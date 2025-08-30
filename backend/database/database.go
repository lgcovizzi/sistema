package database

import (
	"fmt"
	"log"
	"os"
	"time"

	"sistema-backend/models"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

// Connect estabelece conexão com o banco de dados
func Connect() error {
	host := getEnv("DB_HOST", "localhost")
	port := getEnv("DB_PORT", "5432")
	user := getEnv("DB_USER", "sistema_user")
	password := getEnv("DB_PASSWORD", "sistema_password")
	dbname := getEnv("DB_NAME", "sistema_db")

	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=disable TimeZone=UTC",
		host, user, password, dbname, port)

	var err error
	DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
		NowFunc: func() time.Time {
			return time.Now().UTC()
		},
	})

	if err != nil {
		return fmt.Errorf("falha ao conectar com o banco de dados: %w", err)
	}

	// Configurar pool de conexões
	sqlDB, err := DB.DB()
	if err != nil {
		return fmt.Errorf("falha ao obter instância SQL DB: %w", err)
	}

	// Configurações de pool
	sqlDB.SetMaxIdleConns(10)
	sqlDB.SetMaxOpenConns(100)
	sqlDB.SetConnMaxLifetime(time.Hour)

	log.Println("Conectado ao banco de dados PostgreSQL com GORM")
	return nil
}

// Migrate executa as migrações do banco de dados
func Migrate() error {
	err := DB.AutoMigrate(
		&models.User{},
		&models.Product{},
	)

	if err != nil {
		return fmt.Errorf("falha ao executar migrações: %w", err)
	}

	log.Println("Migrações executadas com sucesso")
	return nil
}

// Close fecha a conexão com o banco de dados
func Close() error {
	sqlDB, err := DB.DB()
	if err != nil {
		return err
	}
	return sqlDB.Close()
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}