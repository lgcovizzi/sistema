package main

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

type User struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	Email     string    `json:"email"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type Product struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Price       float64   `json:"price"`
	Stock       int       `json:"stock"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

var backendURL string

func main() {
	backendURL = getEnv("BACKEND_URL", "http://localhost:8080")

	// Configurar Gin
	r := gin.Default()

	// Configurar CORS
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"*"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Carregar templates
	r.LoadHTMLGlob("templates/*")

	// Servir arquivos estáticos
	r.Static("/static", "./static")

	// Rotas
	r.GET("/", homePage)
	r.GET("/dashboard", dashboardPage)
	r.GET("/users", usersPage)
	r.GET("/products", productsPage)
	r.POST("/api/users", createUserProxy)
	r.POST("/api/products", createProductProxy)

	port := getEnv("SERVER_PORT", "3002")
	log.Printf("Frontend Fundador rodando na porta %s", port)
	r.Run(":" + port)
}

func homePage(c *gin.Context) {
	c.HTML(http.StatusOK, "index.html", gin.H{
		"title": "Sistema - Home",
	})
}

func dashboardPage(c *gin.Context) {
	c.HTML(http.StatusOK, "dashboard.html", gin.H{
		"title": "Dashboard",
	})
}

func usersPage(c *gin.Context) {
	// Buscar usuários do backend
	users, err := fetchUsers()
	if err != nil {
		log.Printf("Erro ao buscar usuários: %v", err)
		users = []User{}
	}

	c.HTML(http.StatusOK, "users.html", gin.H{
		"title": "Usuários",
		"users": users,
	})
}

func productsPage(c *gin.Context) {
	// Buscar produtos do backend
	products, err := fetchProducts()
	if err != nil {
		log.Printf("Erro ao buscar produtos: %v", err)
		products = []Product{}
	}

	c.HTML(http.StatusOK, "products.html", gin.H{
		"title": "Produtos",
		"products": products,
	})
}

func createUserProxy(c *gin.Context) {
	// Proxy para o backend
	resp, err := http.Post(backendURL+"/api/users", "application/json", c.Request.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	c.Data(resp.StatusCode, "application/json", body)
}

func createProductProxy(c *gin.Context) {
	// Proxy para o backend
	resp, err := http.Post(backendURL+"/api/products", "application/json", c.Request.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	c.Data(resp.StatusCode, "application/json", body)
}

func fetchUsers() ([]User, error) {
	resp, err := http.Get(backendURL + "/api/users")
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var users []User
	err = json.NewDecoder(resp.Body).Decode(&users)
	return users, err
}

func fetchProducts() ([]Product, error) {
	resp, err := http.Get(backendURL + "/api/products")
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var products []Product
	err = json.NewDecoder(resp.Body).Decode(&products)
	return products, err
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}