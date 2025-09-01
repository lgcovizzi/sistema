# Sistema - Projeto Completo Django

## Visão Geral
Sistema completo de gerenciamento empresarial desenvolvido com Django 5.2, PostgreSQL 15, Redis, Celery, e infraestrutura completa de produção.

## Arquitetura

### Stack Tecnológica
- **Backend**: Django 5.2 (Python 3.11+)
- **Banco de Dados**: PostgreSQL 15 (produção) / PostgreSQL Test (desenvolvimento)
- **Cache**: Redis 6.2
- **Servidor Web**: Nginx com load balancer
- **Processamento Assíncrono**: Celery + Redis
- **Monitoramento**: Grafana, Prometheus, Alertmanager
- **Email**: Mailu (produção) / MailHog (desenvolvimento)
- **SSL**: Let's Encrypt + Certbot

### APIs Disponíveis
- **REST API**: Django REST Framework
- **GraphQL**: Graphene-Django
- **WebSocket**: Django Channels (implementado)
- **JWT Authentication**: Access token (15 min) + Refresh token (366 dias)
- **Token Blacklist**: Sistema de logout seguro
- **Token Persistence**: Refresh token armazenado no cliente

##### Modelos de Dados
- **User**: Usuário principal com autenticação JWT
- **EmailVerificationToken**: Tokens para verificação de email
- **PasswordResetToken**: Tokens para recuperação de senha
- **DeviceSession**: Sessões por dispositivo
- **TokenBlacklist**: Tokens revogados
- **AuditLog**: Registro de ações do sistema
- **UnactivatedAccount**: Contas pendentes de ativação (para soft delete)

#### Campos Adicionais no Modelo User
```python
class User(AbstractUser):
    # Campos existentes...
    email_verified = models.BooleanField(default=False)
    activation_reminders_sent = models.IntegerField(default=0)
    activation_token_created = models.DateTimeField(null=True, blank=True)
    last_activation_email_sent = models.DateTimeField(null=True, blank=True)
    
    def is_activation_expired(self):
        """Verifica se a ativação expirou após 24h"""
        if self.activation_token_created:
            return timezone.now() > self.activation_token_created + timedelta(hours=24)
        return False
```

#### Modelo UnactivatedAccount (Soft Delete)
```python
class UnactivatedAccount(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_registered = models.DateTimeField()
    date_deleted = models.DateTimeField(auto_now_add=True)
    deletion_reason = models.CharField(max_length=100, default="Não ativada em 24h")
    
    class Meta:
        db_table = 'unactivated_accounts'
        
    def __str__(self):
        return f"{self.email} - excluída em {self.date_deleted}"
```

### Estrutura do Projeto

```
sistema/
├── backend/                    # Aplicação Django
│   ├── apps/                   # Aplicações Django
│   │   └── core/              # App principal
│   │       ├── models.py      # Modelos de dados
│   │       ├── views.py       # Views REST e GraphQL
│   │       ├── serializers.py # Serializadores REST
│   │       ├── schema.py      # Schema GraphQL
│   │       └── urls.py        # Rotas da aplicação
│   ├── core/                  # Configuração Django
│   │   ├── settings/          # Configurações por ambiente
│   │   │   ├── base.py       # Configuração base
│   │   │   ├── development.py # Desenvolvimento
│   │   │   └── production.py # Produção
│   │   ├── urls.py           # URLs principais
│   │   └── wsgi.py           # WSGI
│   ├── key_manager.py        # Gerenciamento de chaves
│   ├── backup_manager.py     # Gerenciamento de backup
│   └── keys/                 # Chaves de criptografia
├── mobile/                   # Aplicativo React Native
├── nginx/                    # Configurações Nginx
├── monitoring/              # Configurações de monitoramento
├── scripts/                 # Scripts de automação
└── data/                    # Dados persistentes
```

## Configuração de Ambientes

### Produção (docker-compose.yml)
- **Banco de Dados**: PostgreSQL 15 com alta disponibilidade
- **Cache**: Redis com autenticação
- **Email**: Mailu completo
- **SSL**: Let's Encrypt automático
- **Monitoramento**: Grafana, Prometheus, Alertmanager
- **Backup**: Executado diariamente às 2h

### Desenvolvimento (docker-compose.dev.yml)
- **Banco de Dados**: PostgreSQL Test
- **Cache**: Redis Test
- **Email**: MailHog para captura de emails
- **SSL**: Certificados auto-assinados
- **Debug**: Django Debug Toolbar ativado

## Sistema de Chaves de Criptografia

### Gerenciamento de Chaves
- **Localização**: `/backend/keys/`
- **Tipos de Chaves**:
  - Chave de criptografia (Fernet)
  - Chave de assinatura (RSA 2048)
  - Secret key Django (derivada da chave de criptografia)
- **Ciclo de Vida**: 2 anos
- **Verificação**: Automática no startup
- **Rotação**: Automática quando expiradas ou corrompidas

### Arquivos de Chaves
- `encryption.key`: Chave Fernet para criptografia
- `signing.key`: Chave RSA para assinatura
- `key_metadata.json`: Metadados e validação

## Banco de Dados

### Migrações Automáticas
- Executadas automaticamente no startup do backend
- Verificação de integridade do banco
- Backup automático antes de migrações críticas

### Backup e Restauração
- **Frequência**: Diária às 2h AM
- **Retenção**: 7 dias de backups
- **Compressão**: Gzip
- **Localização**: `/data/backups/`
- **Restauração**: Script automático disponível

### Scripts de Backup
```bash
# Backup manual
./scripts/backup.sh

# Restauração
./scripts/restore.sh [arquivo-backup]
```

## Monitoramento e Alertas

### Stack de Monitoramento
- **Prometheus**: Coleta de métricas
- **Grafana**: Dashboards e visualização
- **Alertmanager**: Gerenciamento de alertas
- **Node Exporter**: Métricas do sistema

### Dashboards Disponíveis
- Sistema operacional (CPU, memória, disco)
- Aplicação Django (requests, erros, performance)
- PostgreSQL (conexões, queries, performance)
- Redis (memória, operações, conexões)
- Celery (tasks, workers, filas)

### Alertas Configurados
- CPU > 80% por 5 minutos
- Memória > 85% por 5 minutos
- Espaço em disco < 10%
- PostgreSQL indisponível
- Redis indisponível
- Backend Django indisponível
- Taxa de erros HTTP > 10%

## Health Checks e Load Balancer

### Health Checks
Todos os containers possuem health checks configurados:
- **PostgreSQL**: Verificação de conectividade
- **Redis**: Teste de ping
- **Django**: Endpoint `/health/` verificando banco e cache
- **Nginx**: Verificação de configuração
- **Celery**: Verificação de workers ativos

### Load Balancer (Nginx)
- **Algoritmo**: Least connections
- **Backend**: 3 instâncias do Django (8000-8002)
- **Failover**: Redirecionamento automático
- **Rate Limiting**: Proteção contra ataques DDoS

## Configurações de Email

### Produção (Mailu)
- **Servidor Completo**: SMTP, IMAP, POP3
- **Autenticação**: LDAP integrado
- **SSL/TLS**: Let's Encrypt automático
- **Webmail**: Roundcube
- **Admin**: Interface web para gerenciamento

### Desenvolvimento (MailHog)
- **Captura de Emails**: Todas as mensagens são capturadas
- **Interface Web**: http://localhost:8025
- **SMTP**: Porta 1025
- **Sem envio real**: Ideal para testes

## Aplicativo Mobile (React Native)

### Estrutura
```
mobile/
├── src/
│   ├── components/     # Componentes reutilizáveis
│   ├── screens/        # Telas do aplicativo
│   ├── services/       # APIs e comunicação
│   ├── store/          # Redux/Context
│   ├── themes/         # Temas claro/escuro
│   ├── hooks/          # Custom hooks
│   └── utils/          # Utilitários
├── app.json           # Configuração do app
├── package.json       # Dependências
└── metro.config.js   # Configuração Metro
```

### Sistema de Temas Claros/Escuros/Responsivos
#### Web (React)
```javascript
// themes/themeContext.js
import React, { createContext, useContext, useEffect, useState } from 'react';

const ThemeContext = createContext();

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }) => {
    const [theme, setTheme] = useState(() => {
        const saved = localStorage.getItem('theme');
        return saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    });

    const [isResponsive, setIsResponsive] = useState(window.innerWidth < 768);

    useEffect(() => {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handleChange = (e) => {
            if (!localStorage.getItem('theme')) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        };
        
        const handleResize = () => setIsResponsive(window.innerWidth < 768);
        
        mediaQuery.addEventListener('change', handleChange);
        window.addEventListener('resize', handleResize);
        
        return () => {
            mediaQuery.removeEventListener('change', handleChange);
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'light' ? 'dark' : 'light');
    };

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme, isResponsive }}>
            {children}
        </ThemeContext.Provider>
    );
};
```

```css
/* themes/styles.css */
:root[data-theme="light"] {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --border-color: #dee2e6;
    --accent-color: #007bff;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
}

:root[data-theme="dark"] {
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --text-primary: #ffffff;
    --text-secondary: #b0b0b0;
    --border-color: #404040;
    --accent-color: #0d6efd;
    --success-color: #198754;
    --danger-color: #dc3545;
    --warning-color: #fd7e14;
}

/* Responsividade */
@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
    
    .sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    
    .sidebar.open {
        transform: translateX(0);
    }
}

@media (min-width: 769px) {
    .container {
        padding: 2rem;
    }
    
    .sidebar {
        transform: none;
    }
}
```

#### Mobile (React Native)
```javascript
// themes/themeManager.js
import { Appearance } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const themes = {
    light: {
        primary: '#007bff',
        background: '#ffffff',
        surface: '#f8f9fa',
        text: '#212529',
        textSecondary: '#6c757d',
        border: '#dee2e6',
        success: '#28a745',
        danger: '#dc3545',
    },
    dark: {
        primary: '#0d6efd',
        background: '#121212',
        surface: '#1e1e1e',
        text: '#ffffff',
        textSecondary: '#b0b0b0',
        border: '#404040',
        success: '#198754',
        danger: '#dc3545',
    }
};

export class ThemeManager {
    static async getTheme() {
        const saved = await AsyncStorage.getItem('theme');
        if (saved) return saved;
        
        const colorScheme = Appearance.getColorScheme();
        return colorScheme || 'light';
    }

    static async setTheme(theme) {
        await AsyncStorage.setItem('theme', theme);
        return themes[theme];
    }

    static getResponsiveStyles(screenWidth) {
        const isTablet = screenWidth >= 768;
        const isSmall = screenWidth < 375;
        
        return {
            fontSize: isSmall ? 14 : isTablet ? 18 : 16,
            padding: isSmall ? 8 : isTablet ? 24 : 16,
            margin: isSmall ? 4 : isTablet ? 12 : 8,
        };
    }
}

// hooks/useTheme.js
import { useState, useEffect } from 'react';
import { useWindowDimensions } from 'react-native';
import { ThemeManager } from '../themes/themeManager';

export const useAppTheme = () => {
    const [theme, setTheme] = useState('light');
    const [colors, setColors] = useState(themes.light);
    const dimensions = useWindowDimensions();
    
    useEffect(() => {
        loadTheme();
    }, []);

    useEffect(() => {
        setColors(themes[theme]);
    }, [theme]);

    const loadTheme = async () => {
        const currentTheme = await ThemeManager.getTheme();
        setTheme(currentTheme);
    };

    const toggleTheme = async () => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        const newColors = await ThemeManager.setTheme(newTheme);
        setTheme(newTheme);
        setColors(newColors);
    };

    const responsive = ThemeManager.getResponsiveStyles(dimensions.width);

    return { theme, colors, toggleTheme, responsive, dimensions };
};
```

#### Componente de Toggle de Tema
```javascript
// components/ThemeToggle.js
import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { useAppTheme } from '../hooks/useTheme';

export const ThemeToggle = () => {
    const { theme, toggleTheme, colors } = useAppTheme();

    return (
        <TouchableOpacity 
            style={[styles.button, { backgroundColor: colors.primary }]} 
            onPress={toggleTheme}
        >
            <Text style={[styles.text, { color: colors.background }]}
                {theme === 'light' ? '🌙' : '☀️'}
            </Text>
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    button: {
        padding: 12,
        borderRadius: 25,
        margin: 8,
    },
    text: {
        fontSize: 20,
    },
});
```

### Funcionalidades
- **Autenticação**: Login com JWT
- **API REST**: Consumo completo das APIs
- **GraphQL**: Queries e mutations
- **Offline**: Cache local com Redux Persist
- **Push Notifications**: Firebase Cloud Messaging
- **Temas Dinâmicos**: Claro/escuro com detecção automática
- **Responsividade**: Adaptação automática para diferentes tamanhos de tela
- **Persistência de Tema**: Lembra a preferência do usuário

## Comandos de Desenvolvimento

### Produção
```bash
# Inicializar o sistema
./setup.sh

# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f [serviço]

# Executar comandos Django
docker-compose exec backend python manage.py [comando]
```

### Desenvolvimento
```bash
# Iniciar ambiente de desenvolvimento
docker-compose -f docker-compose.dev.yml up -d

# Executar testes
docker-compose -f docker-compose.dev.yml exec backend python manage.py test

# Shell Django
docker-compose -f docker-compose.dev.yml exec backend python manage.py shell
```

## Segurança

### Configurações de Segurança
- **HTTPS**: Redirecionamento automático HTTP → HTTPS
- **HSTS**: Strict Transport Security
- **CSP**: Content Security Policy
- **Rate Limiting**: Proteção contra ataques
- **CORS**: Configuração restrita
- **SQL Injection**: Proteção com ORM
- **XSS**: Sanitização automática
- **CSRF**: Proteção completa contra Cross-Site Request Forgery

### CSRF Protection - Implementação Completa
#### Django Backend
```python
# settings.py
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_AGE = 31449600  # 1 ano
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'
CSRF_TRUSTED_ORIGINS = [
    'https://seusistema.com.br',
    'https://www.seusistema.com.br',
]

# Para APIs REST
CSRF_USE_SESSIONS = False
CSRF_COOKIE_NAME = 'csrftoken'
```

#### Frontend - CSRF Token Management
```javascript
// services/csrfService.js
class CSRFService {
    constructor() {
        this.token = null;
        this.refreshToken();
    }

    refreshToken() {
        // Para web
        const cookieToken = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        
        if (cookieToken) {
            this.token = cookieToken.split('=')[1];
        } else {
            // Buscar via endpoint
            this.fetchToken();
        }
    }

    async fetchToken() {
        try {
            const response = await fetch('/api/v1/auth/csrf-token/');
            const data = await response.json();
            this.token = data.csrfToken;
        } catch (error) {
            console.error('Erro ao buscar CSRF token:', error);
        }
    }

    getHeaders() {
        return {
            'X-CSRFToken': this.token,
            'Content-Type': 'application/json',
        };
    }
}

// React Native - CSRF para APIs
const getCSRFToken = async () => {
    const token = await AsyncStorage.getItem('csrfToken');
    if (!token) {
        const response = await API.get('/auth/csrf-token/');
        await AsyncStorage.setItem('csrfToken', response.data.csrfToken);
        return response.data.csrfToken;
    }
    return token;
};
```

#### CSRF Endpoints
```python
# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.middleware.csrf import get_token

@csrf_exempt
def csrf_token(request):
    """Endpoint para obter CSRF token via API"""
    return JsonResponse({'csrfToken': get_token(request)})

# URLs
path('api/v1/auth/csrf-token/', csrf_token, name='csrf-token'),
```

### Chaves e Segredos
- **Secret Key**: Gerada automaticamente e armazenada com criptografia
- **Variáveis de Ambiente**: Todas as configurações sensíveis via env vars
- **SSL**: Certificados Let's Encrypt renovados automaticamente

## Tailwind CSS - Framework de Estilos

### Configuração Web (React)
#### Instalação e Setup
```bash
# Instalar dependências
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

#### Configuração tailwind.config.js
```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  darkMode: 'class', // Habilita dark mode via classe
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a',
        },
        secondary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          900: '#0f172a',
        },
        success: {
          50: '#ecfdf5',
          500: '#10b981',
          600: '#059669',
        },
        danger: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

#### CSS Base com Tailwind
```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    font-family: 'Inter', system-ui, sans-serif;
  }
  
  body {
    @apply bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100;
  }
}

@layer components {
  .btn-primary {
    @apply bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .btn-secondary {
    @apply bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .card {
    @apply bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700;
  }
  
  .input-field {
    @apply w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700;
  }
}

@layer utilities {
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
}
```

#### Componentes Tailwind Responsivos
```javascript
// components/ResponsiveCard.js
import React from 'react';

const ResponsiveCard = ({ children, className = '' }) => {
  return (
    <div className={`card ${className} 
      w-full max-w-4xl mx-auto 
      p-4 sm:p-6 lg:p-8 
      mt-4 sm:mt-6 lg:mt-8`}>
      {children}
    </div>
  );
};

// components/ResponsiveGrid.js
const ResponsiveGrid = ({ children }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
      {children}
    </div>
  );
};

// components/DarkModeToggle.js
const DarkModeToggle = ({ isDark, toggle }) => {
  return (
    <button
      onClick={toggle}
      className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
    >
      {isDark ? (
        <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
        </svg>
      ) : (
        <svg className="w-5 h-5 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
          <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
        </svg>
      )}
    </button>
  );
};
```

### Configuração Mobile (React Native)
#### NativeWind para React Native
```bash
# Instalar NativeWind (Tailwind para React Native)
npm install nativewind
npm install -D tailwindcss@3.3.2
```

#### Configuração tailwind.config.js para Mobile
```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./App.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          900: '#1e3a8a',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
      },
      fontSize: {
        'xs': 12,
        'sm': 14,
        'base': 16,
        'lg': 18,
        'xl': 20,
        '2xl': 24,
        '3xl': 30,
      },
      spacing: {
        '1': 4,
        '2': 8,
        '3': 12,
        '4': 16,
        '5': 20,
        '6': 24,
        '8': 32,
        '10': 40,
        '12': 48,
        '16': 64,
        '20': 80,
        '24': 96,
      },
    },
  },
  plugins: [],
}
```

#### Componentes Tailwind para Mobile
```javascript
// components/TailwindButton.js
import React from 'react';
import { Text, TouchableOpacity } from 'react-native';
import { styled } from 'nativewind';

const StyledTouchableOpacity = styled(TouchableOpacity);
const StyledText = styled(Text);

const TailwindButton = ({ title, variant = 'primary', onPress, className = '' }) => {
  const baseClasses = "px-4 py-2 rounded-lg font-medium text-center";
  const variantClasses = {
    primary: "bg-blue-500 text-white",
    secondary: "bg-gray-200 text-gray-800",
    danger: "bg-red-500 text-white",
    outline: "border border-gray-300 text-gray-700",
  };

  return (
    <StyledTouchableOpacity
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      onPress={onPress}
    >
      <StyledText className="text-center font-medium">{title}</StyledText>
    </StyledTouchableOpacity>
  );
};

// components/ResponsiveCard.js
const ResponsiveCard = ({ children, className = '' }) => {
  return (
    <StyledView className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 ${className}`}>
      {children}
    </StyledView>
  );
};

// components/ResponsiveGrid.js
const ResponsiveGrid = ({ children }) => {
  return (
    <StyledView className="flex flex-row flex-wrap -mx-2">
      {React.Children.map(children, (child, index) => (
        <StyledView key={index} className="w-full sm:w-1/2 md:w-1/3 lg:w-1/4 px-2 mb-4">
          {child}
        </StyledView>
      ))}
    </StyledView>
  );
};
```

### Integração com Temas
#### Tailwind + Dark Mode
```javascript
// hooks/useTailwindTheme.js
import { useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const useTailwindTheme = () => {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    loadTheme();
  }, []);

  const loadTheme = async () => {
    const saved = await AsyncStorage.getItem('tailwind-theme');
    setIsDark(saved === 'dark');
  };

  const toggleTheme = async () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    await AsyncStorage.setItem('tailwind-theme', newTheme ? 'dark' : 'light');
  };

  return { isDark, toggleTheme };
};
```

#### Responsive Breakpoints
```javascript
// utils/responsive.js
export const breakpoints = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
};

export const useResponsive = () => {
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const updateDimensions = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  return {
    isMobile: dimensions.width < breakpoints.sm,
    isTablet: dimensions.width >= breakpoints.sm && dimensions.width < breakpoints.md,
    isDesktop: dimensions.width >= breakpoints.md,
    dimensions,
  };
};
```

### Comandos de Desenvolvimento
```bash
# Desenvolvimento com Tailwind
npm run dev:tailwind    # Watch mode para desenvolvimento
npm run build:tailwind  # Build otimizado para produção
npm run lint:tailwind   # Verificar classes Tailwind

# Mobile com NativeWind
npm run dev:mobile      # Desenvolvimento mobile com hot reload
npm run build:mobile    # Build para produção mobile
```

## Performance

### Otimizações Tailwind
- **PurgeCSS**: Classes não utilizadas são removidas automaticamente
- **Tree-shaking**: Apenas classes utilizadas são incluídas no build final
- **JIT Mode**: Compilação instantânea no desenvolvimento
- **Responsive**: Classes responsivas geradas sob demanda
- **Dark Mode**: Classes dark mode geradas dinamicamente

### Escalabilidade
- **Horizontal**: Múltiplas instâncias do backend
- **Vertical**: Recursos configuráveis via variáveis de ambiente
- **Database**: Preparado para replicação
- **Cache**: Preparado para cluster Redis

## Sistema de Autenticação Completo

### Fluxo de Login
- **Registro**: Criação de conta com validação de email
- **Login**: Autenticação via JWT (access + refresh tokens)
- **Validação de Email**: Link único enviado por email
- **Recuperação de Senha**: Fluxo completo com segurança

### JWT Configuration
- **Access Token**: 15 minutos de validade
- **Refresh Token**: 366 dias de validade
- **Token Storage**: Persistência segura no cliente (localStorage/secure storage)
- **Token Blacklist**: Sistema de logout seguro
- **Auto Refresh**: Renovação automática do access token
- **Remember Me**: Opção para extender validade do refresh token para 1 ano
- **Device Recognition**: Tokens vinculados ao dispositivo para segurança
- **Concurrent Sessions**: Suporte para múltiplos dispositivos simultâneos

### Fluxo de Verificação de Email com Auto Login
1. Registro de novo usuário
2. Envio de email de verificação (rate limit: 5 tentativas/hora por email)
3. Clique no link de verificação
4. **Auto login automático após verificação** - usuário logado instantaneamente
5. Geração de JWT tokens (access + refresh)
6. Persistência automática dos tokens no cliente
7. Redirecionamento para dashboard logado

### Fluxo de Recuperação de Senha com Auto Login
1. Solicitação via email (rate limit: 3 tentativas/hora por IP/usuário)
2. Envio de link único válido por 1 hora
3. Redefinição de senha com validação
4. **Auto login após redefinição** - sem necessidade de novo login
5. Invalidação de tokens antigos
6. Geração de novos JWT tokens
7. Cache Redis para armazenar estado de rate limit
8. Bloqueio temporário de 24h após 10 tentativas falhas

### Rate Limiting Detalhado
- **Recuperação de Senha**: 3 tentativas por hora por email
- **Verificação de Email**: 5 tentativas por hora por email
- **Reenvio de Ativação**: 3 tentativas por dia por email
- **Login**: 5 tentativas por IP/15 minutos
- **Registro**: 3 tentativas por IP/hora
- **Cache TTL**: 1 hora para tokens, 24h para bloqueios

### Cache Redis - Implementação Completa
- **Tokens de Recuperação**: TTL 1 hora, key: `password_reset:{token}`
- **Rate Limit**: TTL 1 hora, key: `rate_limit:{action}:{identifier}`
- **Tokens de Verificação**: TTL 24 horas, key: `email_verify:{token}`
- **Blacklist JWT**: TTL dinâmico (até expiração do token)
- **Cache de Usuário**: TTL 5 minutos, key: `user_cache:{user_id}`
- **Sessões Ativas**: TTL 30 dias, key: `session:{user_id}:{token_id}`
- **Contas Não Ativadas**: TTL 24 horas, key: `unactivated_account:{user_id}`
- **Reenvio de Ativação**: TTL 24 horas, key: `activation_resent:{email}`
- **Lembretes de Ativação**: TTL 24 horas, key: `activation_reminder:{user_id}`

### Sistema de Persistência JWT - Evitar Login Repetido
#### Armazenamento Cliente
- **localStorage**: Para web (com fallback para sessionStorage)
- **AsyncStorage**: Para React Native
- **Secure Storage**: Para mobile nativo
- **HttpOnly Cookies**: Alternativa segura para web
- **Token Encryption**: Tokens criptografados no cliente

#### Mecanismo de Refresh Automático
- **Silent Refresh**: Renovação automática a cada 10 minutos
- **Background Refresh**: Processo assíncrono quando app está inativo
- **On-Demand Refresh**: Verificação antes de requests críticos
- **Fallback Manual**: Prompt de login apenas se refresh falhar

#### Gestão de Sessões
- **Device ID**: Identificador único por dispositivo
- **Session Metadata**: Último acesso, localização, device info
- **Concurrent Sessions**: Lista de dispositivos ativos
- **Remote Logout**: Possibilidade de deslogar dispositivos remotos
- **Session Expiry**: Configurável (30 dias padrão)

#### Integração com Verificação de Email
- **Auto Login pós-verificação**: Tokens gerados automaticamente após clique no link
- **Device Binding**: Token vinculado ao dispositivo que clicou
- **Redirect Automático**: Direcionamento direto para dashboard logado
- **Fallback Seguro**: Se token expirar, redirect para login com mensagem informativa

### Sistema de Gerenciamento de Contas Não Ativadas

#### Limpeza Automática de Contas Não Ativadas
- **Período de Ativação**: 24 horas para ativação do email
- **Limpeza Automática**: Contas não ativadas são removidas automaticamente após 24h
- **Notificação de Exclusão**: Email informando sobre exclusão por inatividade
- **Re-cadastro Permitido**: Usuário pode se cadastrar novamente após exclusão
- **Log de Exclusões**: Registro completo no banco de dados para auditoria

#### Reenvio Automático de Email de Ativação
- **Reenvio Condicional**: Reenvio automático se email não foi ativado após 12 horas
- **Rate Limit**: Máximo 2 reenvios por conta (12h e 20h após registro)
- **Verificação de Status**: Sistema verifica status antes de reenviar
- **Personalização**: Templates diferentes para reenvio vs primeiro envio
- **Tracking**: Monitoramento de taxa de ativação após reenvio

#### Workflow Completo de Ativação
1. **Registro Inicial**: Usuário se cadastra
2. **Primeiro Email**: Envio imediato de email de ativação
3. **Verificação 12h**: Sistema verifica se foi ativado
4. **Reenvio 1**: Se não ativado, reenvio automático em 12h
5. **Verificação 20h**: Segunda verificação
6. **Reenvio 2**: Segundo reenvio automático em 20h
7. **Verificação 24h**: Verificação final
8. **Exclusão Automática**: Conta removida se não ativada
9. **Notificação Final**: Email informando sobre exclusão

#### Configuração do Sistema de Limpeza
- **Celery Beat**: Tarefas agendadas para verificação perióódica
- **Timezone**: UTC configurado para precisão de 24h
- **Soft Delete**: Contas são marcadas como excluídas antes de remoção física
- **Backup**: Backup automático antes de exclusão física
- **Auditoria**: Log completo de todas as exclusões

#### Scripts de Manutenção
**Arquivo**: `/backend/core/tasks.py`
```python
@shared_task
def cleanup_unactivated_accounts():
    """Remove contas não ativadas após 24 horas"""
    cutoff_time = timezone.now() - timedelta(hours=24)
    unactivated = User.objects.filter(
        is_active=False,
        date_joined__lt=cutoff_time,
        email_verified=False
    )
    deleted_count = unactivated.count()
    unactivated.delete()
    return f"{deleted_count} contas não ativadas removidas"

@shared_task
def send_activation_reminder():
    """Reenvia email de ativação após 12 e 20 horas"""
    now = timezone.now()
    
    # Primeiro reenvio (12h)
    first_reminder = now - timedelta(hours=12)
    users_12h = User.objects.filter(
        is_active=False,
        date_joined__range=[first_remedy - timedelta(minutes=30), first_reminder],
        email_verified=False,
        activation_reminders_sent=0
    )
    
    # Segundo reenvio (20h)
    second_reminder = now - timedelta(hours=20)
    users_20h = User.objects.filter(
        is_active=False,
        date_joined__range=[second_reminder - timedelta(minutes=30), second_reminder],
        email_verified=False,
        activation_reminders_sent=1
    )
    
    total_sent = 0
    for user in users_12h | users_20h:
        send_activation_email(user)
        user.activation_reminders_sent += 1
        user.save()
        total_sent += 1
    
    return f"{total_sent} emails de ativação reenviados"
```

#### Configuração Celery Beat
**Arquivo**: `/backend/core/settings.py`
```python
# Tarefas agendadas para gerenciamento de contas
CELERY_BEAT_SCHEDULE = {
    'cleanup-unactivated-accounts': {
        'task': 'core.tasks.cleanup_unactivated_accounts',
        'schedule': crontab(hour=3, minute=0),  # 3h AM diariamente
    },
    'send-activation-reminders': {
        'task': 'core.tasks.send_activation_reminder',
        'schedule': crontab(minute='*/30'),  # A cada 30 minutos
    },
}
```

#### Templates de Email
**Arquivo**: `/backend/templates/email/activation_reminder.html`
```html
<!DOCTYPE html>
<html>
<head>
    <title>Lembrete de Ativação - Sistema</title>
</head>
<body>
    <h2>Olá {{ user.first_name|default:user.username }}!</h2>
    <p>Você se cadastrou no nosso sistema há {{ hours_since_registration }} horas, mas ainda não ativou sua conta.</p>
    <p>Para garantir sua segurança e manter nosso sistema limpo, sua conta será automaticamente excluída em {{ hours_remaining }} horas se não for ativada.</p>
    <p>
        <a href="{{ activation_link }}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Ativar Minha Conta Agora
        </a>
    </p>
    <p>Se você não solicitou este cadastro, por favor ignore este email.</p>
</body>
</html>
```

**Arquivo**: `/backend/templates/email/account_deleted.html`
```html
<!DOCTYPE html>
<html>
<head>
    <title>Conta Excluída - Sistema</title>
</head>
<body>
    <h2>Olá {{ username }}!</h2>
    <p>Conforme nossa política de segurança, sua conta não ativada foi automaticamente excluída após 24 horas do cadastro.</p>
    <p>Se você deseja usar nossos serviços, será necessário realizar um novo cadastro.</p>
    <p>
        <a href="{{ register_link }}" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Criar Nova Conta
        </a>
    </p>
    <p>Obrigado pelo seu interesse em nosso sistema!</p>
</body>
</html>
```

#### Métricas e Monitoramento
- **Taxa de Ativação**: Porcentagem de contas ativadas em 24h
- **Taxa de Reenvio**: Efetividade dos lembretes
- **Tempo Médio de Ativação**: Quanto tempo leva para ativar
- **Exclusões Diárias**: Número de contas removidas
- **Emails Reenviados**: Volume de reenvios por dia

#### Comandos de Gerenciamento
```bash
# Verificar contas não ativadas
python manage.py check_unactivated_accounts

# Forçar limpeza manual
python manage.py cleanup_unactivated_accounts --dry-run
python manage.py cleanup_unactivated_accounts --execute

# Estatísticas de ativação
python manage.py activation_stats

# Reenviar manualmente
python manage.py resend_activation [email@example.com]
```

#### Integração com Recuperação de Senha
- **Auto Login pós-redefinição**: Novos tokens gerados após sucesso
- **Invalidação Total**: Todos os tokens antigos do usuário são revogados
- **Notificação de Segurança**: Email informando sobre novo login
- **Session Migration**: Migração de sessão sem perda de estado

### Sistema de Segurança Avançada Multi-Camadas

#### Nginx - Rate Limiting por IP
- **Limite de Requests**: 100 requests/minuto por IP
- **Burst Allowance**: 50 requests adicionais em burst
- **Zona de Rate Limit**: 10MB para armazenar estados de 16k IPs
- **Endpoints Protegidos**: /api/v1/auth/*, /admin/, /login/
- **Whitelist**: IPs internos e administrativos
- **Custom Headers**: X-RateLimit-Limit, X-RateLimit-Remaining
- **Response Codes**: 429 (Too Many Requests) com retry-after
- **Configuração**:
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;
limit_req zone=api burst=50 nodelay;
```

#### Django-axes - Bloqueio de Contas
- **Tentativas Falhas**: 5 tentativas antes do bloqueio
- **Duração do Bloqueio**: 30 minutos (incremental)
- **Tracking Completo**: Username, IP, user-agent, path
- **Notificações**: Email para administradores em bloqueios
- **Interface Admin**: Dashboard para monitorar tentativas
- **Configuração**:
```python
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 30  # minutos
AXES_LOCKOUT_TEMPLATE = 'account_locked.html'
AXES_LOCKOUT_BY_COMBINATION_USER_AND_IP = True
```

#### Fail2Ban - Bloqueio em Nível de Rede
- **Jails Configurados**: nginx-auth, nginx-login, nginx-api
- **Padrões de Detecção**: 401, 403, 429 HTTP responses
- **Ação**: Bloqueio de IP por 1 hora via iptables
- **Log Monitoring**: /var/log/nginx/access.log
- **Whitelist**: Redes internas confiáveis
- **Notificações**: Email para administração
- **Configuração**:
```ini
[nginx-auth]
enabled = true
filter = nginx-auth
action = iptables-multiport[name=nginx-auth, port="http,https"]
bantime = 3600
maxretry = 5
```

#### Redis - Armazenamento Distribuído de Contadores
- **Estrutura de Dados**: Redis Hash para contadores por IP/username
- **TTL Automático**: Expiração automática após período de bloqueio
- **Atomic Operations**: INCR/DECR para consistência em concorrência
- **Distribuição**: Compartilhado entre múltiplas instâncias Django
- **Persistência**: RDB snapshots para recuperação
- **Monitoramento**: Métricas exportadas para Prometheus
- **Keys Pattern**:
```
rate_limit:ip:{ip_address}:{endpoint}
rate_limit:user:{username}:{endpoint}
failed_logins:ip:{ip_address}
failed_logins:user:{username}
blocked_ips:{ip_address}
```

#### Integração Completa dos Sistemas
- **Fluxo de Trabalho**:
  1. Nginx aplica rate limiting inicial
  2. Django-axes rastreia tentativas falhas
  3. Redis armazena contadores distribuídos
  4. Fail2Ban bloqueia IPs maliciosos
  5. Notificações são enviadas aos administradores

- **Escalabilidade**: Todos os sistemas suportam múltiplas instâncias
- **Monitoramento**: Métricas de todos os sistemas no Grafana
- **Resiliência**: Fallback entre camadas se uma falhar
- **Performance**: Latência < 1ms para verificações

#### Configuração de Exceções e Whitelist
- **Administradores**: Bypass de rate limiting para IPs confiáveis
- **APIs Internas**: Endpoints de health check sem rate limit
- **Mobile Apps**: User-agents específicos com limites diferentes
- **Testes Automatizados**: IPs de CI/CD com limites aumentados

### Arquivos de Configuração de Segurança

#### Nginx Rate Limit Configuration
**Arquivo**: `/nginx/nginx.conf`
```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

# Application of rate limits
location /api/v1/auth/ {
    limit_req zone=auth burst=20 nodelay;
    limit_req_status 429;
    add_header X-RateLimit-Limit $limit_req_limit;
    add_header X-RateLimit-Remaining $limit_req_remaining;
    proxy_pass http://backend;
}

location /admin/ {
    limit_req zone=login burst=10 nodelay;
    limit_req_status 429;
    proxy_pass http://backend;
}
```

#### Django-axes Configuration
**Arquivo**: `/backend/core/settings.py`
```python
# Django-axes settings
INSTALLED_APPS += ['axes']
MIDDLEWARE += ['axes.middleware.AxesMiddleware']

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 30  # minutes
AXES_LOCKOUT_BY_COMBINATION_USER_AND_IP = True
AXES_LOCKOUT_TEMPLATE = 'account_locked.html'
AXES_RESET_ON_SUCCESS = True
AXES_ENABLE_ADMIN = True
AXES_VERBOSE = True

# Redis backend for axes
AXES_CACHE = 'axes'
CACHES['axes'] = {
    'BACKEND': 'django_redis.cache.RedisCache',
    'LOCATION': 'redis://redis:6379/1',
    'OPTIONS': {
        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    }
}
```

#### Fail2Ban Configuration
**Arquivo**: `/monitoring/fail2ban/jail.local`
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
backend = auto
usedns = warn
logencoding = auto
enabled = false
mode = normal
filter = %(name)s[mode=%(mode)s]

[nginx-auth]
enabled = true
filter = nginx-auth
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 5
bantime = 3600

[nginx-login]
enabled = true
filter = nginx-login
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 3
bantime = 7200

[nginx-api]
enabled = true
filter = nginx-api
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 10
bantime = 1800
```

**Arquivo**: `/monitoring/fail2ban/filter.d/nginx-auth.conf`
```ini
[Definition]
failregex = ^<HOST>.*"(?:GET|POST|HEAD).*(?:/api/v1/auth/).*" (?:401|403|429)
ignoreregex =
```

#### Redis Security Schema
**Arquivo**: `/scripts/redis-security-setup.sh`
```bash
#!/bin/bash
# Setup Redis security keys and TTLs

redis-cli << EOF
# Rate limiting keys with TTL
SET rate_limit:config:ttl 3600
SET rate_limit:config:max_attempts 5
SET rate_limit:config:window 300

# Fail2Ban coordination
SET fail2ban:config:sync true
SET fail2ban:config:ttl 3600

# Whitelist configuration
SADD whitelist:ips 127.0.0.1 10.0.0.0/8 192.168.0.0/16
EOF
```

### Monitoramento de Segurança

#### Dashboards Grafana
- **Nginx Rate Limits**: Taxa de requests bloqueados
- **Django-axes Blocks**: Contas bloqueadas e tentativas
- **Fail2Ban Activity**: IPs banidos e atividade suspeita
- **Redis Security Metrics**: Uso de memória e chaves TTL

#### Alertas de Segurança
- **Ataque em Massa**: >100 tentativas de login/minuto
- **Bloqueios Frequentes**: >10 bloqueios em 5 minutos
- **IPs Suspeitos**: Múltiplos bloqueios do mesmo IP
- **Redis Indisponível**: Falha no backend de rate limiting

### Setup e Deploy

#### Instalação de Dependências
```bash
# Fail2Ban
sudo apt-get install fail2ban

# Django-axes
pip install django-axes

# Redis security tools
pip install redis django-redis
```

#### Configuração Inicial
```bash
# Setup Fail2Ban
sudo cp monitoring/fail2ban/jail.local /etc/fail2ban/
sudo systemctl restart fail2ban

# Setup Redis security keys
./scripts/redis-security-setup.sh

# Verificar status
sudo fail2ban-client status nginx-auth
sudo fail2ban-client status nginx-login
```

#### Testes de Segurança
```bash
# Testar rate limiting
ab -n 100 -c 10 http://localhost/api/v1/auth/login/

# Testar bloqueio de conta
for i in {1..6}; do curl -X POST http://localhost/api/v1/auth/login/ -d '{}'; done

# Verificar logs
sudo fail2ban-client get nginx-auth bantime
sudo fail2ban-client get nginx-auth maxretry
```

### Endpoints de Autenticação
- `POST /api/v1/auth/register/` - Registro de novo usuário
- `POST /api/v1/auth/login/` - Login com JWT
- `POST /api/v1/auth/refresh/` - Renovação de access token
- `POST /api/v1/auth/logout/` - Logout com blacklist
- `GET /api/v1/auth/verify-email/{token}/` - Verificação de email com auto login
- `POST /api/v1/auth/password-reset/` - Solicitar recuperação
- `POST /api/v1/auth/password-reset-confirm/{token}/` - Confirmar recuperação com auto login
- `GET /api/v1/auth/me/` - Informações do usuário logado
- `GET /api/v1/auth/sessions/` - Listar sessões ativas do usuário
- `DELETE /api/v1/auth/sessions/{session_id}/` - Encerrar sessão específica
- `POST /api/v1/auth/remember-me/` - Extender validade do refresh token
- `POST /api/v1/auth/resend-activation/` - Solicitar reenvio de email de ativação
- `GET /api/v1/auth/activation-status/` - Verificar status de ativação da conta

## Documentação das APIs

### REST API
- **Endpoint**: `/api/v1/`
- **Autenticação**: JWT Bearer Token
- **Formato**: JSON
- **Paginação**: Limit/offset
- **Filtros**: Query parameters
- **Documentação**: Swagger/OpenAPI

### GraphQL
- **Endpoint**: `/graphql/`
- **Interface**: GraphiQL em desenvolvimento
- **Autenticação**: Header Authorization
- **Schema**: Introspecção disponível
- **Subscrições**: Preparado para WebSocket

## Manutenção

### Atualizações
- **Zero Downtime**: Rolling updates
- **Backup**: Antes de cada atualização
- **Rollback**: Rápido em caso de problemas
- **Testes**: Suite completa de testes

### Monitoramento de Logs
- **Centralizado**: Todos os logs em /var/log/
- **Rotação**: Logrotate configurado
- **Análise**: ELK Stack preparado
- **Alertas**: Erros críticos notificados

## Suporte e Troubleshooting

### Comandos Úteis
```bash
# Verificar saúde do sistema
docker-compose ps

# Logs detalhados
docker-compose logs -f [serviço]

# Reiniciar serviço específico
docker-compose restart [serviço]

# Limpar cache Redis
docker-compose exec redis redis-cli FLUSHALL

# Verificar espaço em disco
df -h
```

### Problemas Comuns
- **Portas em uso**: Verificar com `netstat -tlnp`
- **Permissões**: Executar `sudo chown -R $USER:$USER data/`
- **SSL**: Verificar certificados em `data/certbot/conf/`
- **Backup**: Verificar logs em `data/backups/`

## Ambientes de Deploy

### Desenvolvimento
- **URL**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/v1/
- **GraphQL**: http://localhost:8000/graphql/
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Flower**: http://localhost:5555
- **MailHog**: http://localhost:8025

### Produção
- **URL**: https://localhost
- **API**: https://localhost/api/v1/
- **GraphQL**: https://localhost/graphql/
- **Admin**: https://localhost/admin/
- **Monitoramento**: https://localhost:8080/
- **Email**: https://localhost/mailu/

## Contribuição

### Desenvolvimento
1. Clone o repositório
2. Configure ambiente de desenvolvimento
3. Crie branch para feature
4. Desenvolva com testes
5. Submeta pull request

### Padrões de Código
- **PEP 8**: Python style guide
- **Black**: Formatação automática
- **MyPy**: Type checking
- **Pre-commit**: Hooks de qualidade
- **Tests**: Pytest com cobertura > 80%

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

---

**Última atualização**: 2024
**Versão**: 1.0.0
**Autor**: Sistema Team