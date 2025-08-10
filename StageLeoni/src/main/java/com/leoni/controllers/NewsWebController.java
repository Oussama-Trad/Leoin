package com.leoni.controllers;

import com.leoni.models.Admin;
import com.leoni.models.SuperAdmin;
import com.leoni.models.News;
import com.leoni.services.AdminService;
import com.leoni.services.SuperAdminService;
import com.leoni.services.NewsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@Controller
@RequestMapping("/news")
public class NewsWebController {

    @Autowired
    private AdminService adminService;
    
    @Autowired
    private SuperAdminService superAdminService;
    
    @Autowired
    private NewsService newsService;

    @GetMapping
    public String news(Model model, @RequestParam(required = false) String adminUsername) {
        System.out.println("NewsWebController: Called with adminUsername=" + adminUsername);
        
        try {
            // 1. Determine admin role and filtering
            boolean isSuperAdmin = false;
            String adminDepartment = null;
            String adminLocation = null;
            String displayName = adminUsername != null ? adminUsername : "Test Admin";
            String role = "ADMIN";
            
            // Check if admin exists in database and get role/location/department
            if (adminUsername != null) {
                try {
                    // First check in regular admins
                    Optional<Admin> adminOpt = adminService.findByUsername(adminUsername);
                    if (adminOpt.isPresent()) {
                        Admin admin = adminOpt.get();
                        isSuperAdmin = "SUPERADMIN".equals(admin.getRole());
                        adminDepartment = admin.getDepartment();
                        adminLocation = admin.getLocation();
                        displayName = admin.getUsername() + " (" + admin.getRole() + ")";
                        role = admin.getRole();
                        System.out.println("Found admin: " + displayName + ", Department: " + adminDepartment + ", Location: " + adminLocation + ", IsSuperAdmin: " + isSuperAdmin);
                    } else {
                        // Check in superadmins collection
                        Optional<SuperAdmin> superAdminOpt = superAdminService.findByUsername(adminUsername);
                        if (superAdminOpt.isPresent()) {
                            SuperAdmin superAdmin = superAdminOpt.get();
                            isSuperAdmin = true;
                            role = "SUPERADMIN";
                            displayName = superAdmin.getUsername() + " (SUPERADMIN)";
                            System.out.println("Found superadmin: " + displayName);
                        } else {
                            System.out.println("Admin/SuperAdmin '" + adminUsername + "' not found in database, using demo mode");
                            // Demo mode - assume regular admin
                            adminDepartment = "Production";
                            adminLocation = "Mateur";
                            displayName = adminUsername + " (Demo Admin)";
                        }
                    }
                } catch (Exception e) {
                    System.err.println("Error fetching admin info: " + e.getMessage());
                    // Fallback to demo mode
                    adminDepartment = "Production";
                    adminLocation = "Mateur";
                    displayName = adminUsername + " (Fallback)";
                }
            }
            
            // 2. Fetch and filter news based on role
            List<News> filteredNews;
            
            if (isSuperAdmin) {
                // SuperAdmin sees all news
                filteredNews = newsService.getAllNews();
                System.out.println("SuperAdmin - showing all " + filteredNews.size() + " news");
            } else {
                // Regular admin sees only their department and location news
                filteredNews = newsService.getFilteredNews(adminLocation, adminDepartment);
                System.out.println("Regular admin - filtered to " + filteredNews.size() + " news items");
            }
            
            // 3. Calculate statistics
            long totalNews = filteredNews.size();
            long publishedNews = filteredNews.stream()
                .filter(news -> news.getIsActive())
                .count();
            long draftNews = filteredNews.stream()
                .filter(news -> !news.getIsActive())
                .count();
            
            // 4. Set model attributes
            model.addAttribute("adminUsername", adminUsername);
            model.addAttribute("adminDisplayName", displayName);
            model.addAttribute("isSuperAdmin", isSuperAdmin);
            model.addAttribute("adminDepartment", adminDepartment);
            model.addAttribute("adminLocation", adminLocation);
            model.addAttribute("role", role);
            
            model.addAttribute("news", filteredNews);
            model.addAttribute("totalNews", totalNews);
            model.addAttribute("publishedNews", publishedNews);
            model.addAttribute("draftNews", draftNews);
            
            model.addAttribute("title", "Gestion des Actualités");
            model.addAttribute("currentPage", "news");
            
            System.out.println("News page loaded successfully for: " + displayName);
            return "news";
            
        } catch (Exception e) {
            System.err.println("News error: " + e.getMessage());
            e.printStackTrace();
            
            // Error fallback
            model.addAttribute("error", "Erreur lors du chargement des actualités: " + e.getMessage());
            model.addAttribute("adminUsername", adminUsername);
            model.addAttribute("adminDisplayName", adminUsername != null ? adminUsername : "Utilisateur");
            model.addAttribute("isSuperAdmin", false);
            model.addAttribute("news", List.of());
            model.addAttribute("totalNews", 0);
            model.addAttribute("publishedNews", 0);
            model.addAttribute("draftNews", 0);
            model.addAttribute("title", "Gestion des Actualités - Erreur");
            model.addAttribute("currentPage", "news");
            
            return "news";
        }
    }
}
