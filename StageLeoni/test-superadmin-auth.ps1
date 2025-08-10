# Test d'authentification SuperAdmin
$baseUrl = "http://localhost:8080"

# Données de connexion SuperAdmin
$loginData = @{
    username = "superadmin"
    password = "superadmin123"
} | ConvertTo-Json

Write-Host "=== Test d'authentification SuperAdmin ===" -ForegroundColor Green

try {
    # Test de connexion
    Write-Host "1. Test de connexion..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method POST -Body $loginData -ContentType "application/json"
    
    Write-Host "Réponse:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3 | Write-Host
    
    if ($response.success -eq $true) {
        $token = $response.token
        Write-Host "✅ Connexion réussie! Token: $token" -ForegroundColor Green
        
        # Test de validation du token
        Write-Host "`n2. Test de validation du token..." -ForegroundColor Yellow
        $validateResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/validate?token=$token" -Method POST
        
        Write-Host "Validation:" -ForegroundColor Cyan
        $validateResponse | ConvertTo-Json -Depth 3 | Write-Host
        
        if ($validateResponse.success -eq $true) {
            Write-Host "✅ Token valide!" -ForegroundColor Green
        } else {
            Write-Host "❌ Token invalide!" -ForegroundColor Red
        }
        
        # Test d'accès à la page news
        Write-Host "`n3. Test d'accès à la page news..." -ForegroundColor Yellow
        $newsUrl = "$baseUrl/news?adminUsername=superadmin"
        Write-Host "URL: $newsUrl" -ForegroundColor Cyan
        
        # Note: ceci testera juste que la page se charge sans erreur 500
        try {
            $newsResponse = Invoke-WebRequest -Uri $newsUrl -Method GET
            Write-Host "✅ Page news accessible! Code: $($newsResponse.StatusCode)" -ForegroundColor Green
        } catch {
            Write-Host "❌ Erreur d'accès à la page news: $($_.Exception.Message)" -ForegroundColor Red
        }
        
    } else {
        Write-Host "❌ Échec de la connexion: $($response.message)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Erreur lors du test: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Détails: $($_.Exception.Response)" -ForegroundColor Red
}

Write-Host "`n=== Fin du test ===" -ForegroundColor Green
