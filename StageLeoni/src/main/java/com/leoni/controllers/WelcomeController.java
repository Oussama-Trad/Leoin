package com.leoni.controllers;

import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
public class WelcomeController {

    // Home mapping moved to WebController to avoid conflicts

    // Login mapping moved to WebController to avoid conflicts
    
    @GetMapping("/admin/login")
    public String adminLogin() {
        return "login";
    }
    
    /**
     * Handle favicon.ico requests to prevent 500 errors
     */
    @GetMapping("/favicon.ico")
    @ResponseBody
    public ResponseEntity<Void> favicon() {
        return ResponseEntity.notFound().build();
    }
}
