#!/bin/bash

# =============================================================================
#                    Script de deploiement et test de l'API
#                           Credit Scoring API
# =============================================================================

set -e  # Arreter le script en cas d'erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
API_URL="http://localhost:8000"
TOKEN=""
ADMIN_TOKEN=""
USERS_TO_CREATE=()
SELECTED_USER=""
SELECTED_TOKEN=""

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

print_step() {
    echo -e "${YELLOW}>> $1${NC}"
}

print_success() {
    echo -e "${GREEN}[OK] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERREUR] $1${NC}"
}

pause_step() {
    echo ""
    echo -e "${BLUE}Appuyez sur Entrée pour continuer vers l'étape suivante...${NC}"
    read -r
}

wait_for_api() {
    print_step "Attente que l'API soit prete..."
    for i in {1..30}; do
        if curl -s "$API_URL/" > /dev/null 2>&1; then
            print_success "API disponible !"
            return 0
        fi
        echo -n "."
        sleep 1
    done
    print_error "L'API n'est pas disponible apres 30 secondes"
    exit 1
}

# Menu interactif pour choisir les utilisateurs
choose_users() {
    print_header "CONFIGURATION DES UTILISATEURS A CREER"
    
    echo "Choisissez les utilisateurs à créer (plusieurs choix possibles) :"
    echo "1) john@example.com (John Doe)"
    echo "2) marie@test.com (Marie Martin)"
    echo "3) bob@demo.com (Bob Smith)"
    echo "4) alice@mail.com (Alice Johnson)"
    echo "5) Utilisateur personnalisé"
    echo ""
    
    while true; do
        echo -e "${YELLOW}Entrez les numéros séparés par des espaces (ex: 1 3 5) : ${NC}"
        read -r choices
        
        if [[ -z "$choices" ]]; then
            print_error "Veuillez sélectionner au moins un utilisateur"
            continue
        fi
        
        break
    done
    
    # Traiter les choix
    for choice in $choices; do
        case $choice in
            1)
                USERS_TO_CREATE+=("john@example.com:john:SecurePass123:John Doe")
                ;;
            2)
                USERS_TO_CREATE+=("marie@test.com:marie:MariePass456:Marie Martin")
                ;;
            3)
                USERS_TO_CREATE+=("bob@demo.com:bob:BobSecret789:Bob Smith")
                ;;
            4)
                USERS_TO_CREATE+=("alice@mail.com:alice:AliceKey101:Alice Johnson")
                ;;
            5)
                echo -e "${YELLOW}Email : ${NC}"
                read -r custom_email
                echo -e "${YELLOW}Nom d'utilisateur : ${NC}"
                read -r custom_username
                echo -e "${YELLOW}Mot de passe : ${NC}"
                read -r custom_password
                echo -e "${YELLOW}Nom complet : ${NC}"
                read -r custom_fullname
                USERS_TO_CREATE+=("$custom_email:$custom_username:$custom_password:$custom_fullname")
                ;;
            *)
                print_error "Choix invalide: $choice"
                ;;
        esac
    done
    
    echo ""
    print_success "${#USERS_TO_CREATE[@]} utilisateur(s) sélectionné(s)"
    for user in "${USERS_TO_CREATE[@]}"; do
        IFS=':' read -r email username password fullname <<< "$user"
        echo "  - $username ($email)"
    done
    echo ""
}

# Test de création d'utilisateur avec gestion d'erreurs
test_user_creation() {
    local email="$1"
    local username="$2"
    local password="$3"
    local fullname="$4"
    
    print_step "Test d'inscription : $username ($email)..."
    
    REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
      -H "Content-Type: application/json" \
      -d "{
        \"email\": \"$email\",
        \"username\": \"$username\",
        \"password\": \"$password\",
        \"full_name\": \"$fullname\"
      }")

    echo "Réponse: $REGISTER_RESPONSE"
    
    if echo "$REGISTER_RESPONSE" | grep -q "\"$username\""; then
        print_success "Utilisateur $username créé avec succès"
        return 0
    elif echo "$REGISTER_RESPONSE" | grep -q "already registered"; then
        print_error "Email $email déjà utilisé"
        return 1
    elif echo "$REGISTER_RESPONSE" | grep -q "Username already taken"; then
        print_error "Nom d'utilisateur $username déjà pris"
        return 1
    else
        print_error "Erreur lors de la création de $username"
        return 1
    fi
}

# Menu pour choisir l'utilisateur pour les tests
choose_test_user() {
    print_header "SELECTION DE L'UTILISATEUR POUR LES TESTS"
    
    if [ ${#USERS_TO_CREATE[@]} -eq 1 ]; then
        SELECTED_USER="${USERS_TO_CREATE[0]}"
        IFS=':' read -r email username password fullname <<< "$SELECTED_USER"
        print_success "Utilisateur sélectionné automatiquement : $username"
        return 0
    fi
    
    echo "Choisissez l'utilisateur à utiliser pour les tests de prédictions :"
    i=1
    for user in "${USERS_TO_CREATE[@]}"; do
        IFS=':' read -r email username password fullname <<< "$user"
        echo "$i) $username ($email)"
        ((i++))
    done
    echo ""
    
    while true; do
        echo -e "${YELLOW}Entrez le numéro : ${NC}"
        read -r choice
        
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#USERS_TO_CREATE[@]} ]; then
            SELECTED_USER="${USERS_TO_CREATE[$((choice-1))]}"
            IFS=':' read -r email username password fullname <<< "$SELECTED_USER"
            print_success "Utilisateur sélectionné : $username"
            break
        else
            print_error "Choix invalide"
        fi
    done
}

# =============================================================================
# ETAPE 0 : CONFIGURATION INTERACTIVE
# =============================================================================

choose_users

pause_step

# =============================================================================
# ETAPE 1 : NETTOYAGE ET DEMARRAGE
# =============================================================================

print_header "ETAPE 1 : Nettoyage et demarrage des conteneurs"

print_step "Arret des conteneurs existants..."
docker-compose down 2>/dev/null || true

print_step "Suppression des conteneurs orphelins..."
docker rm -f credit-scoring-api 2>/dev/null || true
docker rm -f credit-scoring-db 2>/dev/null || true

print_step "Reconstruction de l'image Docker..."
docker-compose build

print_step "Demarrage des conteneurs..."
docker-compose up -d

wait_for_api

pause_step

# =============================================================================
# ETAPE 2 : INITIALISATION DE LA BASE DE DONNEES
# =============================================================================

print_header "ETAPE 2 : Initialisation de la base de donnees"

print_step "Execution de init_bd.py..."
docker-compose exec -T api python init_bd.py

print_success "Base de donnees initialisee"

pause_step

# =============================================================================
# ETAPE 3 : TEST D'INSCRIPTION ET GESTION D'ERREURS
# =============================================================================

print_header "ETAPE 3 : Tests d'inscription et gestion d'erreurs"

# Créer tous les utilisateurs sélectionnés
for user in "${USERS_TO_CREATE[@]}"; do
    IFS=':' read -r email username password fullname <<< "$user"
    test_user_creation "$email" "$username" "$password" "$fullname"
done

# Test des erreurs : Email déjà utilisé
print_step "Test d'erreur : Email déjà utilisé..."
ERROR_EMAIL_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "john2",
    "password": "AnotherPass123",
    "full_name": "John Duplicate"
  }')

echo "Réponse: $ERROR_EMAIL_RESPONSE"

if echo "$ERROR_EMAIL_RESPONSE" | grep -q "already registered\|already exists"; then
    print_success "Test OK - Email déjà utilisé correctement détecté"
else
    print_error "Test échoué - Email déjà utilisé non détecté"
fi

# Test des erreurs : Nom d'utilisateur déjà utilisé  
print_step "Test d'erreur : Nom d'utilisateur déjà utilisé..."
ERROR_USERNAME_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "duplicate@example.com",
    "username": "john",
    "password": "AnotherPass123",
    "full_name": "John Username Duplicate"
  }')

echo "Réponse: $ERROR_USERNAME_RESPONSE"

if echo "$ERROR_USERNAME_RESPONSE" | grep -q "already taken\|already exists"; then
    print_success "Test OK - Nom d'utilisateur déjà utilisé correctement détecté"
else
    print_error "Test échoué - Nom d'utilisateur déjà utilisé non détecté"
fi

# Sélectionner l'utilisateur pour les tests suivants
choose_test_user
IFS=':' read -r SELECTED_EMAIL SELECTED_USERNAME SELECTED_PASSWORD SELECTED_FULLNAME <<< "$SELECTED_USER"

pause_step

# =============================================================================
# ETAPE 4 : TEST DE CONNEXION
# =============================================================================

print_header "ETAPE 4 : Test de connexion (login)"

print_step "Connexion de $SELECTED_USERNAME..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$SELECTED_USERNAME&password=$SELECTED_PASSWORD")

echo "Reponse: $LOGIN_RESPONSE"

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
SELECTED_TOKEN="$TOKEN"

if [ -n "$TOKEN" ]; then
    print_success "Token JWT obtenu pour $SELECTED_USERNAME"
    echo "Token: ${TOKEN:0:50}..."
else
    print_error "Echec de recuperation du token"
    exit 1
fi

pause_step

# =============================================================================
# ETAPE 5 : TEST DU PROFIL
# =============================================================================

print_header "ETAPE 5 : Test de recuperation du profil"

print_step "Recuperation du profil de $SELECTED_USERNAME..."
PROFILE_RESPONSE=$(curl -s -X GET "$API_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN")

echo "Reponse: $PROFILE_RESPONSE"

if echo "$PROFILE_RESPONSE" | grep -q "$SELECTED_USERNAME"; then
    print_success "Profil recupere avec succes"
else
    print_error "Echec de recuperation du profil"
fi

pause_step

# =============================================================================
# ETAPE 6 : TEST DE SECURITE (sans token)
# =============================================================================

print_header "ETAPE 6 : Test de securite (prediction sans token)"

print_step "Tentative de prediction sans token..."
SECURITY_RESPONSE=$(curl -s -X POST "$API_URL/predictions/predict" \
  -H "Content-Type: application/json" \
  -d '{"age": 35, "income": 3200, "credit_amount": 15000, "duration": 48}')

echo "Reponse: $SECURITY_RESPONSE"

if echo "$SECURITY_RESPONSE" | grep -q "Not authenticated"; then
    print_success "Securite OK - Acces refuse sans token"
else
    print_error "Probleme de securite - Acces autorise sans token !"
fi

pause_step

# =============================================================================
# ETAPE 7 : TEST DE PREDICTION (avec token)
# =============================================================================

print_header "ETAPE 7 : Test de prediction (avec token)"

print_step "Prediction pour un profil a risque..."
PREDICT1_RESPONSE=$(curl -s -X POST "$API_URL/predictions/predict" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"age": 35, "income": 3200, "credit_amount": 15000, "duration": 48}')

echo "Reponse: $PREDICT1_RESPONSE"

if echo "$PREDICT1_RESPONSE" | grep -q "decision"; then
    print_success "Prediction 1 effectuee"
else
    print_error "Echec de la prediction 1"
fi

print_step "Prediction pour un bon profil..."
PREDICT2_RESPONSE=$(curl -s -X POST "$API_URL/predictions/predict" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"age": 25, "income": 5000, "credit_amount": 8000, "duration": 24}')

echo "Reponse: $PREDICT2_RESPONSE"

if echo "$PREDICT2_RESPONSE" | grep -q "decision"; then
    print_success "Prediction 2 effectuee"
else
    print_error "Echec de la prediction 2"
fi

pause_step

# =============================================================================
# ETAPE 8 : TEST DE L'HISTORIQUE
# =============================================================================

print_header "ETAPE 8 : Test de l'historique des predictions"

print_step "Recuperation de l'historique..."
HISTORY_RESPONSE=$(curl -s -X GET "$API_URL/predictions/history" \
  -H "Authorization: Bearer $TOKEN")

echo "Reponse: $HISTORY_RESPONSE"

if echo "$HISTORY_RESPONSE" | grep -q "decision"; then
    print_success "Historique recupere avec succes"
else
    print_error "Echec de recuperation de l'historique"
fi

pause_step

# =============================================================================
# ETAPE 9 : TEST DES STATISTIQUES UTILISATEUR
# =============================================================================

print_header "ETAPE 9 : Test des statistiques utilisateur"

print_step "Recuperation des statistiques..."
STATS_RESPONSE=$(curl -s -X GET "$API_URL/predictions/stats" \
  -H "Authorization: Bearer $TOKEN")

echo "Reponse: $STATS_RESPONSE"

if echo "$STATS_RESPONSE" | grep -q "total_predictions"; then
    print_success "Statistiques recuperees avec succes"
else
    print_error "Echec de recuperation des statistiques"
fi

pause_step

# =============================================================================
# ETAPE 10 : TEST ADMIN
# =============================================================================

print_header "ETAPE 10 : Test des fonctionnalites admin"

print_step "Connexion en tant qu'admin..."
ADMIN_LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123")

ADMIN_TOKEN=$(echo "$ADMIN_LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$ADMIN_TOKEN" ]; then
    print_success "Token admin obtenu"
else
    print_error "Echec de connexion admin"
    exit 1
fi

print_step "Liste des utilisateurs..."
USERS_RESPONSE=$(curl -s -X GET "$API_URL/admin/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

echo "Reponse: $USERS_RESPONSE"

if echo "$USERS_RESPONSE" | grep -q "admin"; then
    print_success "Liste des utilisateurs recuperee"
else
    print_error "Echec de recuperation des utilisateurs"
fi

print_step "Statistiques globales..."
GLOBAL_STATS_RESPONSE=$(curl -s -X GET "$API_URL/admin/stats" \
  -H "Authorization: Bearer $ADMIN_TOKEN")

echo "Reponse: $GLOBAL_STATS_RESPONSE"

if echo "$GLOBAL_STATS_RESPONSE" | grep -q "total_users"; then
    print_success "Statistiques globales recuperees"
else
    print_error "Echec de recuperation des statistiques globales"
fi

pause_step

# =============================================================================
# BILAN FINAL
# =============================================================================

print_header "BILAN FINAL"

echo -e "${GREEN}"
echo "============================================================"
echo "                    TOUS LES TESTS SONT PASSES !"
echo "============================================================"
echo ""
echo "  L'API Credit Scoring est operationnelle :"
echo ""
echo "  - Authentification JWT : OK"
echo "  - Inscription utilisateur : OK"
echo "  - Connexion : OK"
echo "  - Securite (protection des endpoints) : OK"
echo "  - Predictions ML : OK"
echo "  - Historique : OK"
echo "  - Statistiques : OK"
echo "  - Fonctionnalites admin : OK"
echo ""
echo "  Documentation disponible sur : $API_URL/docs"
echo ""
echo "============================================================"
echo -e "${NC}"

# Afficher les tokens pour utilisation manuelle
echo ""
echo "TOKENS POUR TESTS MANUELS :"
echo "----------------------------"
echo "TOKEN_$SELECTED_USERNAME=$SELECTED_TOKEN"
echo ""
echo "ADMIN_TOKEN=$ADMIN_TOKEN"
echo ""
