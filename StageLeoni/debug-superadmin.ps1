# Script de débogage pour l'authentification SuperAdmin
$baseUrl = "http://localhost:8080"

Write-Host "=== Débogage authentification SuperAdmin ===" -ForegroundColor Green

# 1. Test de base de données
Write-Host "1. Test MongoDB - vérification de la connexion..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/health" -Method GET
    Write-Host "✅ Service d'auth opérationnel: $($healthResponse.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Service d'auth non disponible" -ForegroundColor Red
    exit 1
}

# 2. Test d'authentification détaillé
Write-Host "`n2. Test authentification SuperAdmin..." -ForegroundColor Yellow
$loginData = @{
    username = "superadmin"
    password = "superadmin123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method POST -Body $loginData -ContentType "application/json"
    Write-Host "Réponse complète:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3 | Write-Host
    
    if ($response.success -eq $true) {
        $token = $response.token
        Write-Host "✅ Token généré: $token" -ForegroundColor Green
        
        # Analyse du token
        Write-Host "`n3. Analyse du token..." -ForegroundColor Yellow
        $tokenParts = $token.Split('-')
        Write-Host "Parties du token:" -ForegroundColor Cyan
        for ($i = 0; $i -lt $tokenParts.Length; $i++) {
            Write-Host "  [$i]: $($tokenParts[$i])" -ForegroundColor White
        }
        
        # Test de validation
        Write-Host "`n4. Test de validation du token..." -ForegroundColor Yellow
        try {
            $validateResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/validate?token=$token" -Method POST
            Write-Host "Validation:" -ForegroundColor Cyan
            $validateResponse | ConvertTo-Json -Depth 3 | Write-Host
        } catch {
            Write-Host "❌ Erreur validation: $($_.Exception.Message)" -ForegroundColor Red
        }
        
        # Test récupération des infos utilisateur
        Write-Host "`n5. Test info utilisateur..." -ForegroundColor Yellow
        try {
            $userInfoResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/user-info" -Method GET -Headers @{Authorization = "Bearer $token"}
            Write-Host "Info utilisateur:" -ForegroundColor Cyan
            $userInfoResponse | ConvertTo-Json -Depth 3 | Write-Host
        } catch {
            Write-Host "❌ Erreur info utilisateur: $($_.Exception.Message)" -ForegroundColor Red
        }
        
    } else {
        Write-Host "❌ Échec authentification: $($response.message)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Erreur requête: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Corps de la réponse: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n=== Fin du débogage ===" -ForegroundColor Green
