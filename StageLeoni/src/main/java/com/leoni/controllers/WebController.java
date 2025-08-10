package com.leoni.controllers;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class WebController {
    
    /**
     * Page d'accueil - redirige vers login
     */
    @GetMapping("/")
    public String home() {
        return "redirect:/login";
    }
    
    /**
     * Page de connexion unifiée
     */
    @GetMapping("/login")
    public String loginPage(Model model) {
        model.addAttribute("title", "Leoni Admin - Connexion");
        return "login-unified";
    }
    
    /**
     * Route pour login.html (pour la compatibilité)
     */
    @GetMapping("/login.html")
    public String loginHtmlPage(Model model) {
        model.addAttribute("title", "Leoni Admin - Connexion");
        return "login-unified";
    }
    
    // Dashboard mapping has been moved to UnifiedDashboardController
    // to avoid ambiguous mapping conflicts
    
    /**
     * Page d'erreur personnalisée
     */
    @GetMapping("/error")
    public String errorPage(Model model) {
        model.addAttribute("title", "Erreur");
        model.addAttribute("message", "Une erreur s'est produite");
        return "error";
    }
    
    /**
     * Health check pour vérifier que l'application fonctionne
     */
    @GetMapping("/health")
    public String healthCheck(Model model) {
        model.addAttribute("status", "OK");
        model.addAttribute("message", "Application Leoni Admin fonctionne correctement");
        model.addAttribute("timestamp", java.time.LocalDateTime.now().toString());
        return "health";
    }
}
