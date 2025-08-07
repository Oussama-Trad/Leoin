package com.leoni.controllers;

import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
public class WelcomeController {

    @GetMapping("/")
    public String welcome(Model model) {
        model.addAttribute("title", "Admin Service");
        model.addAttribute("message", "Welcome to Leoni Admin Service");
        return "welcome";
    }

    @GetMapping("/login")
    public String login() {
        // Redirect to home page since login is on the main page
        return "redirect:/";
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
