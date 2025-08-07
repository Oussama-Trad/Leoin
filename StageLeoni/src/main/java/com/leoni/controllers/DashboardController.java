package com.leoni.controllers;

import com.leoni.models.Admin;
import com.leoni.services.AdminService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.Optional;

@Controller
@RequestMapping("/dashboard")
public class DashboardController {

    @Autowired
    private AdminService adminService;

    @GetMapping
    public String dashboard(Model model) {
        model.addAttribute("title", "Leoni Admin Dashboard");
        model.addAttribute("message", "Welcome to the Admin Dashboard");
        return "dashboard";
    }
    
    /**
     * Handle favicon.ico requests to prevent 500 errors
     */
    @GetMapping("/favicon.ico")
    @ResponseBody
    public ResponseEntity<Void> favicon() {
        return ResponseEntity.notFound().build();
    }
    
    /**
     * Get admin information by admin ID (used as session token)
     * @param adminId the admin ID from session
     * @return Admin information
     */
    @GetMapping("/api/admin-info/{adminId}")
    @ResponseBody
    public ResponseEntity<?> getAdminInfo(@PathVariable String adminId) {
        try {
            Optional<Admin> admin = adminService.findById(adminId);
            if (admin.isPresent()) {
                Admin adminInfo = admin.get();
                return ResponseEntity.ok(Map.of(
                    "success", true,
                    "admin", Map.of(
                        "id", adminInfo.getId(),
                        "username", adminInfo.getUsername(),
                        "departmentId", adminInfo.getDepartmentId(),
                        "role", adminInfo.getRole()
                    )
                ));
            } else {
                return ResponseEntity.status(404).body(
                    Map.of("success", false, "message", "Admin not found")
                );
            }
        } catch (Exception e) {
            return ResponseEntity.status(500).body(
                Map.of("success", false, "message", "Error retrieving admin info: " + e.getMessage())
            );
        }
    }
}
