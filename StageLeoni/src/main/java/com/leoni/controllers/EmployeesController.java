package com.leoni.controllers;

import com.leoni.models.Admin;
import com.leoni.models.User;
import com.leoni.services.AdminService;
import com.leoni.repositories.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Controller
@RequestMapping("/employees")
public class EmployeesController {

    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private AdminService adminService;

    @GetMapping
    public String employees(Model model, @RequestParam(required = false) String adminUsername) {
        System.out.println("EmployeesController: Called with adminUsername=" + adminUsername);
        
        try {
            // 1. Determine admin role and filtering
            boolean isSuperAdmin = false;
            String adminDepartment = null;
            String adminLocation = null;
            String displayName = adminUsername != null ? adminUsername : "Test Admin";
            
            // Check if admin exists in database and get role/location/department
            if (adminUsername != null) {
                try {
                    Optional<Admin> adminOpt = adminService.findByUsername(adminUsername);
                    if (adminOpt.isPresent()) {
                        Admin admin = adminOpt.get();
                        isSuperAdmin = "SUPERADMIN".equals(admin.getRole());
                        adminDepartment = admin.getDepartment();
                        adminLocation = admin.getLocation();
                        displayName = admin.getUsername() + " (" + admin.getRole() + ")";
                        System.out.println("Found admin: " + displayName + ", Department: " + adminDepartment + ", Location: " + adminLocation + ", IsSuperAdmin: " + isSuperAdmin);
                    } else {
                        System.out.println("Admin '" + adminUsername + "' not found in database, using demo mode");
                        // Demo mode - assume regular admin
                        adminDepartment = "Production";
                        adminLocation = "Mateur";
                        displayName = adminUsername + " (Demo Admin)";
                    }
                } catch (Exception e) {
                    System.err.println("Error fetching admin info: " + e.getMessage());
                    // Fallback to demo mode
                    adminDepartment = "Production";
                    adminLocation = "Mateur";
                    displayName = adminUsername + " (Fallback)";
                }
            }
            
            // 2. Fetch and filter employees based on role
            List<User> allEmployees = userRepository.findAll();
            List<User> filteredEmployees;
            
            if (isSuperAdmin) {
                // SuperAdmin sees all employees
                filteredEmployees = allEmployees;
                System.out.println("SuperAdmin - showing all " + allEmployees.size() + " employees");
            } else {
                // Regular admin sees only their department and location
                // Capture final values for lambda
                final String finalAdminDepartment = adminDepartment;
                final String finalAdminLocation = adminLocation;
                
                filteredEmployees = allEmployees.stream()
                    .filter(emp -> {
                        boolean deptMatch = (finalAdminDepartment == null || finalAdminDepartment.equals(emp.getDepartment()));
                        boolean locMatch = (finalAdminLocation == null || finalAdminLocation.equals(emp.getLocation()));
                        return deptMatch && locMatch;
                    })
                    .collect(Collectors.toList());
                System.out.println("Regular admin - filtered to " + filteredEmployees.size() + " employees from " + allEmployees.size() + " total");
            }
            
            // 3. Calculate statistics
            long totalEmployees = filteredEmployees.size();
            long activeEmployees = filteredEmployees.stream()
                .filter(emp -> "approved".equals(emp.getStatus()))
                .count();
            long pendingEmployees = filteredEmployees.stream()
                .filter(emp -> "pending".equals(emp.getStatus()))
                .count();
            
            // 4. Set model attributes
            model.addAttribute("adminUsername", adminUsername);
            model.addAttribute("adminDisplayName", displayName);
            model.addAttribute("isSuperAdmin", isSuperAdmin);
            model.addAttribute("adminDepartment", adminDepartment);
            model.addAttribute("adminLocation", adminLocation);
            
            model.addAttribute("employees", filteredEmployees);
            model.addAttribute("totalEmployees", totalEmployees);
            model.addAttribute("activeEmployees", activeEmployees);
            model.addAttribute("pendingEmployees", pendingEmployees);
            
            model.addAttribute("title", "Gestion des Employés");
            model.addAttribute("currentPage", "employees");
            
            System.out.println("Employees page loaded successfully for: " + displayName);
            return "employees";
            
        } catch (Exception e) {
            System.err.println("Employees error: " + e.getMessage());
            e.printStackTrace();
            
            // Error fallback
            model.addAttribute("error", "Erreur lors du chargement des employés: " + e.getMessage());
            model.addAttribute("adminUsername", adminUsername);
            model.addAttribute("adminDisplayName", adminUsername != null ? adminUsername : "Utilisateur");
            model.addAttribute("isSuperAdmin", false);
            model.addAttribute("employees", List.of());
            model.addAttribute("totalEmployees", 0);
            model.addAttribute("activeEmployees", 0);
            model.addAttribute("pendingEmployees", 0);
            model.addAttribute("title", "Gestion des Employés - Erreur");
            model.addAttribute("currentPage", "employees");
            
            return "employees";
        }
    }
}
