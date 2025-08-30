package graph

import (
	"context"
	"fmt"
	"sistema-backend/graph/generated"
	"sistema-backend/graph/model"
	"sistema-backend/models"
	"sistema-backend/database"
)

// CreateUser is the resolver for the createUser field.
func (r *mutationResolver) CreateUser(ctx context.Context, input model.NewUser) (*models.User, error) {
	user := &models.User{
		Name:     input.Name,
		Email:    input.Email,
		Password: input.Password,
	}

	if err := database.DB.Create(user).Error; err != nil {
		return nil, fmt.Errorf("failed to create user: %v", err)
	}

	return user, nil
}

// UpdateUser is the resolver for the updateUser field.
func (r *mutationResolver) UpdateUser(ctx context.Context, id string, input model.UpdateUser) (*models.User, error) {
	// Parse UUID from string
	if id == "" {
		return nil, fmt.Errorf("invalid user ID: empty")
	}

	var user models.User
	if err := database.DB.First(&user, "id = ?", id).Error; err != nil {
		return nil, fmt.Errorf("user not found: %v", err)
	}

	if input.Name != nil {
		user.Name = *input.Name
	}
	if input.Email != nil {
		user.Email = *input.Email
	}

	if err := database.DB.Save(&user).Error; err != nil {
		return nil, fmt.Errorf("failed to update user: %v", err)
	}

	return &user, nil
}

// DeleteUser is the resolver for the deleteUser field.
func (r *mutationResolver) DeleteUser(ctx context.Context, id string) (bool, error) {
	// Parse UUID from string
	if id == "" {
		return false, fmt.Errorf("invalid user ID: empty")
	}

	if err := database.DB.Delete(&models.User{}, "id = ?", id).Error; err != nil {
		return false, fmt.Errorf("failed to delete user: %v", err)
	}

	return true, nil
}

// CreateProduct is the resolver for the createProduct field.
func (r *mutationResolver) CreateProduct(ctx context.Context, input model.NewProduct) (*models.Product, error) {
	product := &models.Product{
		Name:        input.Name,
		Description: "",
		Price:       input.Price,
		Stock:       input.Stock,
	}
	
	if input.Description != nil {
		product.Description = *input.Description
	}

	if err := database.DB.Create(product).Error; err != nil {
		return nil, fmt.Errorf("failed to create product: %v", err)
	}

	return product, nil
}

// UpdateProduct is the resolver for the updateProduct field.
func (r *mutationResolver) UpdateProduct(ctx context.Context, id string, input model.UpdateProduct) (*models.Product, error) {
	// Parse UUID from string
	if id == "" {
		return nil, fmt.Errorf("invalid product ID: empty")
	}

	var product models.Product
	if err := database.DB.First(&product, "id = ?", id).Error; err != nil {
		return nil, fmt.Errorf("product not found: %v", err)
	}

	if input.Name != nil {
		product.Name = *input.Name
	}
	if input.Description != nil {
		product.Description = *input.Description
	}
	if input.Price != nil {
		product.Price = *input.Price
	}
	if input.Stock != nil {
		product.Stock = *input.Stock
	}

	if err := database.DB.Save(&product).Error; err != nil {
		return nil, fmt.Errorf("failed to update product: %v", err)
	}

	return &product, nil
}

// DeleteProduct is the resolver for the deleteProduct field.
func (r *mutationResolver) DeleteProduct(ctx context.Context, id string) (bool, error) {
	// Parse UUID from string
	if id == "" {
		return false, fmt.Errorf("invalid product ID: empty")
	}

	if err := database.DB.Delete(&models.Product{}, "id = ?", id).Error; err != nil {
		return false, fmt.Errorf("failed to delete product: %v", err)
	}

	return true, nil
}

// Users is the resolver for the users field.
func (r *queryResolver) Users(ctx context.Context) ([]*models.User, error) {
	var users []*models.User
	if err := database.DB.Find(&users).Error; err != nil {
		return nil, fmt.Errorf("failed to fetch users: %v", err)
	}
	return users, nil
}

// User is the resolver for the user field.
func (r *queryResolver) User(ctx context.Context, id string) (*models.User, error) {
	// Parse UUID from string
	if id == "" {
		return nil, fmt.Errorf("invalid user ID: empty")
	}

	var user models.User
	if err := database.DB.First(&user, "id = ?", id).Error; err != nil {
		return nil, fmt.Errorf("user not found: %v", err)
	}

	return &user, nil
}

// Products is the resolver for the products field.
func (r *queryResolver) Products(ctx context.Context) ([]*models.Product, error) {
	var products []*models.Product
	if err := database.DB.Find(&products).Error; err != nil {
		return nil, fmt.Errorf("failed to fetch products: %v", err)
	}
	return products, nil
}

// Product is the resolver for the product field.
func (r *queryResolver) Product(ctx context.Context, id string) (*models.Product, error) {
	// Parse UUID from string
	if id == "" {
		return nil, fmt.Errorf("invalid product ID: empty")
	}

	var product models.Product
	if err := database.DB.First(&product, "id = ?", id).Error; err != nil {
		return nil, fmt.Errorf("product not found: %v", err)
	}

	return &product, nil
}

// Mutation returns generated.MutationResolver implementation.
func (r *Resolver) Mutation() generated.MutationResolver { return &mutationResolver{r} }

// Query returns generated.QueryResolver implementation.
func (r *Resolver) Query() generated.QueryResolver { return &queryResolver{r} }

type mutationResolver struct{ *Resolver }
type queryResolver struct{ *Resolver }