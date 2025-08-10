# Test rapide des corrections
Write-Host "=== Test des corrections ===" -ForegroundColor Green

# Vérifier que l'application est en cours d'exécution
$baseUrl = "http://localhost:8080"

try {
    Write-Host "1. Test de connectivité..." -ForegroundColor Yellow
    $health = Invoke-RestMethod -Uri "$baseUrl/api/auth/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Application accessible" -ForegroundColor Green
} catch {
    Write-Host "❌ Application non accessible. Assurez-vous qu'elle est démarrée." -ForegroundColor Red
    Write-Host "Lancez: ./mvnw spring-boot:run" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n2. Test authentification SuperAdmin..." -ForegroundColor Yellow
$loginData = @{
    username = "superadmin"
    password = "superadmin123"
} | ConvertTo-Json

try {
    $authResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method POST -Body $loginData -ContentType "application/json"
    
    if ($authResponse.success) {
        Write-Host "✅ SuperAdmin connecté avec succès!" -ForegroundColor Green
        Write-Host "Token: $($authResponse.token)" -ForegroundColor Cyan
        Write-Host "Rôle: $($authResponse.role)" -ForegroundColor Cyan
        
        # Test page actualités
        Write-Host "`n3. Test page actualités..." -ForegroundColor Yellow
        try {
            $newsResponse = Invoke-WebRequest -Uri "$baseUrl/news?adminUsername=superadmin" -Method GET
            if ($newsResponse.StatusCode -eq 200) {
                Write-Host "✅ Page actualités accessible!" -ForegroundColor Green
            } else {
                Write-Host "❌ Erreur page actualités: $($newsResponse.StatusCode)" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Erreur page actualités: $($_.Exception.Message)" -ForegroundColor Red
        }
        
    } else {
        Write-Host "❌ Échec connexion SuperAdmin: $($authResponse.message)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Erreur lors de l'authentification: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Code de statut: $($_.Exception.Response.StatusCode.Value__)" -ForegroundColor Red
    }
}

Write-Host "`n=== Fin du test ===" -ForegroundColor Green
Write-Host "Si des erreurs persistent, vérifiez les logs de l'application." -ForegroundColor Yellow
