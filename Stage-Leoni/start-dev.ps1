# Script PowerShell pour démarrer l'environnement de développement Leoni App
# Utilisation: .\start-dev.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "     LEONI APP - DEMARRAGE DEVELOPPEMENT" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si ngrok est installé
try {
    $ngrokVersion = & ngrok version
    Write-Host "✅ Ngrok détecté: $ngrokVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ngrok n'est pas installé ou pas dans le PATH" -ForegroundColor Red
    Write-Host "💡 Installation:" -ForegroundColor Yellow
    Write-Host "   - Téléchargez ngrok: https://ngrok.com/download" -ForegroundColor Yellow
    Write-Host "   - Ou installez avec: choco install ngrok" -ForegroundColor Yellow
    Write-Host "   - Ou installez avec: npm install -g ngrok" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continuer sans ngrok? (y/N)"
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        exit 1
    }
}

Write-Host "[1/3] Démarrage du serveur backend Flask..." -ForegroundColor Blue
$backendPath = Join-Path $PSScriptRoot "Backend"
if (Test-Path $backendPath) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python app.py"
    Write-Host "✅ Serveur backend démarré dans une nouvelle fenêtre" -ForegroundColor Green
} else {
    Write-Host "❌ Dossier Backend non trouvé!" -ForegroundColor Red
    exit 1
}

Write-Host "[2/3] Attente de 5 secondes pour que le serveur démarre..." -ForegroundColor Blue
Start-Sleep -Seconds 5

Write-Host "[3/3] Démarrage de ngrok..." -ForegroundColor Blue
try {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "ngrok http 5000"
    Write-Host "✅ Ngrok démarré dans une nouvelle fenêtre" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Impossible de démarrer ngrok automatiquement" -ForegroundColor Yellow
    Write-Host "💡 Démarrez manuellement: ngrok http 5000" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "     CONFIGURATION TERMINEE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host "1. Attendez que ngrok affiche une URL HTTPS" -ForegroundColor White
Write-Host "2. Copiez cette URL (ex: https://abc123.ngrok.io)" -ForegroundColor White
Write-Host "3. Ouvrez l'app mobile Expo Go" -ForegroundColor White
Write-Host "4. Cliquez sur l'icône paramètres (⚙️) sur l'écran de connexion" -ForegroundColor White
Write-Host "5. Collez l'URL ngrok et cliquez 'Mettre à jour l'URL'" -ForegroundColor White
Write-Host "6. Testez la connexion" -ForegroundColor White
Write-Host ""
Write-Host "⚠️ REMARQUE:" -ForegroundColor Red
Write-Host "L'URL ngrok change à chaque redémarrage!" -ForegroundColor Red
Write-Host "Pour une URL fixe, créez un compte gratuit sur ngrok.com" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔧 DÉPANNAGE:" -ForegroundColor Magenta
Write-Host "- Si ça ne marche pas, vérifiez l'IP locale dans config.js" -ForegroundColor White
Write-Host "- L'IP actuelle de cette machine:" -ForegroundColor White

# Afficher l'IP locale
try {
    $ip = (Get-NetIPAddress | Where-Object { $_.AddressFamily -eq "IPv4" -and $_.InterfaceAlias -ne "Loopback Pseudo-Interface 1" }).IPAddress | Select-Object -First 1
    Write-Host "   📍 $ip" -ForegroundColor Cyan
    Write-Host "   📝 Modifiez config.js si nécessaire: 'http://$ip:5000'" -ForegroundColor Yellow
} catch {
    Write-Host "   ❌ Impossible de détecter l'IP automatiquement" -ForegroundColor Red
    Write-Host "   💡 Utilisez 'ipconfig' pour trouver votre IP" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
