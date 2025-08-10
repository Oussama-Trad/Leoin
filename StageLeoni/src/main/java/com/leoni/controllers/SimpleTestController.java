package com.leoni.controllers;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class SimpleTestController {

    @GetMapping("/test")
    public String testPage(Model model) {
        model.addAttribute("message", "Test simple sans MongoDB!");
        return "test-simple";
    }

    @GetMapping("/simple")
    public String homePage(Model model) {
        model.addAttribute("title", "Leoni Admin - Test");
        model.addAttribute("message", "Application fonctionnelle sans MongoDB");
        return "welcome";
    }
}
