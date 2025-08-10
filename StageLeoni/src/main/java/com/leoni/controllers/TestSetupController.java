package com.leoni.controllers;

import com.leoni.models.Admin;
import com.leoni.models.SuperAdmin;
import com.leoni.models.User;
import com.leoni.services.AdminService;
import com.leoni.services.SuperAdminService;
import com.leoni.repositories.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/test-setup")
@CrossOrigin(origins = "*")
public class TestSetupController {

    @Autowired
    private AdminService adminService;

    @Autowired
    private SuperAdminService superAdminService;

    @Autowired
    private UserRepository userRepository;
    
    /**
     * Create specific test admin 'trad' for testing
     */
    @PostMapping("/create-trad-admin")
    public ResponseEntity<Map<String, Object>> createTradAdmin() {
        try {
            Map<String, Object> response = new HashMap<>();
            
            // Create 'trad' admin for Production/Mateur
            Admin tradAdmin = new Admin();
            tradAdmin.setUsername("trad");
            tradAdmin.setPassword("admin123"); // Will be hashed by service
            tradAdmin.setEmail("trad@leoni.com");
            // firstName and lastName not available in Admin model
            tradAdmin.setLocation("Mateur");
            tradAdmin.setDepartment("Production");
            tradAdmin.setRole("ADMIN");
            tradAdmin.setActive(true);
            tradAdmin.setCreatedAt(LocalDateTime.now());
            tradAdmin.setUpdatedAt(LocalDateTime.now());
            
            Admin savedTradAdmin = adminService.save(tradAdmin);
            response.put("tradAdmin", Map.of(
                "id", savedTradAdmin.getId(),
                "username", savedTradAdmin.getUsername(),
                "email", savedTradAdmin.getEmail(),
                "location", savedTradAdmin.getLocation(),
                "department", savedTradAdmin.getDepartment(),
                "role", savedTradAdmin.getRole()
            ));
            
            // Also create some employees for this admin to manage
            for (int i = 1; i <= 5; i++) {
                User employee = new User();
                employee.setFirstName("Trad-Employee" + i);
                employee.setLastName("Worker");
                employee.setAdresse1("trad.emp" + i + "@leoni.com");
                employee.setEmployeeId("TRAD_PROD_" + String.format("%03d", i));
                employee.setPosition("Production Worker " + i);
                employee.setPhoneNumber("+21671237" + String.format("%03d", i));
                employee.setLocation("Mateur");
                employee.setDepartment("Production");
                employee.setStatus("approved");
                employee.setCreatedAt(new Date());
                employee.setUpdatedAt(new Date());
                
                userRepository.save(employee);
            }
            
            response.put("message", "Trad admin and employees created successfully");
            response.put("employees", "5 employees created for Production/Mateur that 'trad' admin can manage");
            response.put("loginInfo", Map.of(
                "url", "http://localhost:9999/dashboard?adminUsername=trad",
                "username", "trad",
                "department", "Production",
                "location", "Mateur"
            ));
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Failed to create trad admin: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(error);
        }
    }

    /**
     * Create test admin and superadmin accounts
     */
    @PostMapping("/create-test-accounts")
    public ResponseEntity<Map<String, Object>> createTestAccounts() {
        try {
            Map<String, Object> response = new HashMap<>();
            
            // Create SuperAdmin account
            SuperAdmin superAdmin = new SuperAdmin();
            superAdmin.setUsername("superadmin");
            superAdmin.setPassword("superadmin123");
            superAdmin.setEmail("superadmin@leoni.com");
            superAdmin.setFirstName("Super");
            superAdmin.setLastName("Administrator");
            superAdmin.setActive(true);
            
            SuperAdmin savedSuperAdmin = superAdminService.createSuperAdmin(superAdmin);
            response.put("superAdmin", Map.of(
                "id", savedSuperAdmin.getId(),
                "username", savedSuperAdmin.getUsername(),
                "email", savedSuperAdmin.getEmail(),
                "role", savedSuperAdmin.getRole()
            ));

            // Create Admin account for Messadine/Production
            Admin adminMessadine = new Admin();
            adminMessadine.setUsername("admin_messadine");
            adminMessadine.setPassword("admin123");
            adminMessadine.setEmail("admin.messadine@leoni.com");
            adminMessadine.setLocation("Messadine");
            adminMessadine.setDepartment("Production");
            adminMessadine.setRole("ADMIN");
            adminMessadine.setActive(true);
            adminMessadine.setCreatedAt(LocalDateTime.now());
            adminMessadine.setUpdatedAt(LocalDateTime.now());
            
            Admin savedAdminMessadine = adminService.save(adminMessadine);
            response.put("adminMessadine", Map.of(
                "id", savedAdminMessadine.getId(),
                "username", savedAdminMessadine.getUsername(),
                "email", savedAdminMessadine.getEmail(),
                "location", savedAdminMessadine.getLocation(),
                "department", savedAdminMessadine.getDepartment(),
                "role", savedAdminMessadine.getRole()
            ));

            // Create Admin account for Mateur/Quality Control
            Admin adminMateur = new Admin();
            adminMateur.setUsername("admin_mateur");
            adminMateur.setPassword("admin123");
            adminMateur.setEmail("admin.mateur@leoni.com");
            adminMateur.setLocation("Mateur");
            adminMateur.setDepartment("Quality Control");
            adminMateur.setRole("ADMIN");
            adminMateur.setActive(true);
            adminMateur.setCreatedAt(LocalDateTime.now());
            adminMateur.setUpdatedAt(LocalDateTime.now());
            
            Admin savedAdminMateur = adminService.save(adminMateur);
            response.put("adminMateur", Map.of(
                "id", savedAdminMateur.getId(),
                "username", savedAdminMateur.getUsername(),
                "email", savedAdminMateur.getEmail(),
                "location", savedAdminMateur.getLocation(),
                "department", savedAdminMateur.getDepartment(),
                "role", savedAdminMateur.getRole()
            ));

            response.put("message", "Test accounts created successfully");
            response.put("instructions", Map.of(
                "superAdmin", "Login with username: superadmin, password: superadmin123",
                "adminMessadine", "Login with username: admin_messadine, password: admin123 (sees only Messadine/Production employees)",
                "adminMateur", "Login with username: admin_mateur, password: admin123 (sees only Mateur/Quality Control employees)"
            ));

            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Failed to create test accounts: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(error);
        }
    }

    /**
     * Create test employees with different locations and departments
     */
    @PostMapping("/create-test-employees")
    public ResponseEntity<Map<String, Object>> createTestEmployees() {
        try {
            Map<String, Object> response = new HashMap<>();
            int employeeCount = 0;

            // Create employees for Messadine/Production
            for (int i = 1; i <= 3; i++) {
                User employee = new User();
                employee.setFirstName("John" + i);
                employee.setLastName("Messadine");
                employee.setAdresse1("john" + i + ".messadine@leoni.com");
                employee.setEmployeeId("MESS_PROD_" + String.format("%03d", i));
                employee.setPosition("Production Worker " + i);
                employee.setPhoneNumber("+21671234" + String.format("%03d", i));
                employee.setLocation("Messadine");
                employee.setDepartment("Production");
                employee.setStatus("approved");
                employee.setCreatedAt(new Date());
                employee.setUpdatedAt(new Date());
                
                userRepository.save(employee);
                employeeCount++;
            }

            // Create employees for Mateur/Quality Control
            for (int i = 1; i <= 3; i++) {
                User employee = new User();
                employee.setFirstName("Jane" + i);
                employee.setLastName("Mateur");
                employee.setAdresse1("jane" + i + ".mateur@leoni.com");
                employee.setEmployeeId("MAT_QC_" + String.format("%03d", i));
                employee.setPosition("Quality Inspector " + i);
                employee.setPhoneNumber("+21671235" + String.format("%03d", i));
                employee.setLocation("Mateur");
                employee.setDepartment("Quality Control");
                employee.setStatus("approved");
                employee.setCreatedAt(new Date());
                employee.setUpdatedAt(new Date());
                
                userRepository.save(employee);
                employeeCount++;
            }

            // Create employees for Sousse/Engineering  
            for (int i = 1; i <= 2; i++) {
                User employee = new User();
                employee.setFirstName("Ahmed" + i);
                employee.setLastName("Sousse");
                employee.setAdresse1("ahmed" + i + ".sousse@leoni.com");
                employee.setEmployeeId("SOU_ENG_" + String.format("%03d", i));
                employee.setPosition("Software Engineer " + i);
                employee.setPhoneNumber("+21671236" + String.format("%03d", i));
                employee.setLocation("Sousse");
                employee.setDepartment("Engineering");
                employee.setStatus("approved");
                employee.setCreatedAt(new Date());
                employee.setUpdatedAt(new Date());
                
                userRepository.save(employee);
                employeeCount++;
            }

            response.put("message", "Test employees created successfully");
            response.put("employeesCreated", employeeCount);
            response.put("locations", Map.of(
                "Messadine", "3 employees in Production department",
                "Mateur", "3 employees in Quality Control department", 
                "Sousse", "2 employees in Engineering department"
            ));
            response.put("testScenarios", Map.of(
                "admin_messadine", "Will see only the 3 Messadine/Production employees",
                "admin_mateur", "Will see only the 3 Mateur/Quality Control employees",
                "superadmin", "Will see all 8 employees and can filter by location/department"
            ));

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Failed to create test employees: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body(error);
        }
    }

    /**
     * Get summary of test data
     */
    @GetMapping("/test-summary")
    public ResponseEntity<Map<String, Object>> getTestSummary() {
        try {
            Map<String, Object> summary = new HashMap<>();
            
            // Count total employees by location and department
            long totalEmployees = userRepository.count();
            summary.put("totalEmployees", totalEmployees);
            
            long messadineEmployees = userRepository.findAll().stream()
                .filter(emp -> "Messadine".equals(emp.getLocation()) && "Production".equals(emp.getDepartment()))
                .count();
            
            long mateurEmployees = userRepository.findAll().stream()
                .filter(emp -> "Mateur".equals(emp.getLocation()) && "Quality Control".equals(emp.getDepartment()))
                .count();
                
            long sousseEmployees = userRepository.findAll().stream()
                .filter(emp -> "Sousse".equals(emp.getLocation()) && "Engineering".equals(emp.getDepartment()))
                .count();

            summary.put("employeeBreakdown", Map.of(
                "messadineProduction", messadineEmployees,
                "mateurQualityControl", mateurEmployees,
                "sousseEngineering", sousseEmployees
            ));

            summary.put("testInstructions", Map.of(
                "step1", "Use POST /api/test-setup/create-test-accounts to create admin accounts",
                "step2", "Use POST /api/test-setup/create-test-employees to create test employees", 
                "step3", "Login with different admin accounts to test role-based filtering:",
                "superadmin", "superadmin / superadmin123 - sees all employees",
                "adminMessadine", "admin_messadine / admin123 - sees only Messadine/Production", 
                "adminMateur", "admin_mateur / admin123 - sees only Mateur/Quality Control"
            ));

            return ResponseEntity.ok(summary);

        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Failed to get test summary: " + e.getMessage());
            return ResponseEntity.status(500).body(error);
        }
    }

    /**
     * Clean up test data
     */
    @DeleteMapping("/cleanup-test-data")
    public ResponseEntity<Map<String, Object>> cleanupTestData() {
        try {
            // Delete test employees
            userRepository.findAll().stream()
                .filter(emp -> emp.getEmployeeId() != null && 
                    (emp.getEmployeeId().startsWith("MESS_PROD_") || 
                     emp.getEmployeeId().startsWith("MAT_QC_") ||
                     emp.getEmployeeId().startsWith("SOU_ENG_")))
                .forEach(emp -> userRepository.delete(emp));

            // Delete test admins  
            adminService.findByUsername("admin_messadine").ifPresent(admin -> adminService.deleteAdmin(admin.getId()));
            adminService.findByUsername("admin_mateur").ifPresent(admin -> adminService.deleteAdmin(admin.getId()));
            
            // Delete test superadmin
            superAdminService.findByUsername("superadmin").ifPresent(sa -> superAdminService.deleteSuperAdmin(sa.getId()));

            Map<String, Object> response = new HashMap<>();
            response.put("message", "Test data cleaned up successfully");
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "Failed to cleanup test data: " + e.getMessage());
            return ResponseEntity.status(500).body(error);
        }
    }
}
