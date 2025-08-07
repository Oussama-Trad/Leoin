package com.leoni.controllers;

import com.leoni.models.Department;
import com.leoni.repositories.DepartmentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/departments")
@CrossOrigin(origins = "*")
public class DepartmentController {

    @Autowired
    private DepartmentRepository departmentRepository;

    /**
     * Get all departments
     */
    @GetMapping
    public ResponseEntity<List<Department>> getAllDepartments() {
        try {
            List<Department> departments = departmentRepository.findAll();
            return ResponseEntity.ok(departments);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Get departments by location (replaces level-based filtering)
     */
    @GetMapping("/location/{location}")
    public ResponseEntity<List<Department>> getDepartmentsByLocationEndpoint(@PathVariable String location) {
        try {
            List<Department> departments = departmentRepository.findByLocation(location);
            return ResponseEntity.ok(departments);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Get simplified department structure grouped by location
     */
    @GetMapping("/structure")
    public ResponseEntity<Map<String, Object>> getDepartmentStructure() {
        try {
            List<Department> allDepartments = departmentRepository.findAll();
            
            // Group departments by location
            Map<String, List<Map<String, Object>>> departmentsByLocation = allDepartments.stream()
                    .collect(Collectors.groupingBy(
                            Department::getLocation,
                            Collectors.mapping(this::departmentToMap, Collectors.toList())
                    ));
            
            return ResponseEntity.ok(Map.of(
                "success", true,
                "departmentsByLocation", departmentsByLocation,
                "totalDepartments", allDepartments.size(),
                "locations", departmentsByLocation.keySet().stream().sorted().collect(Collectors.toList())
            ));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                Map.of("success", false, "message", "Error fetching department structure")
            );
        }
    }

    /**
     * Create a new department with simplified structure
     */
    @PostMapping
    public ResponseEntity<?> createDepartment(@RequestBody Department department) {
        try {
            // Check for duplicates with same name and location
            if (departmentRepository.existsByNameAndLocation(department.getName(), department.getLocation())) {
                return ResponseEntity.badRequest().body("Department with this name already exists at this location");
            }

            Department savedDepartment = departmentRepository.save(department);
            return ResponseEntity.ok(savedDepartment);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error creating department");
        }
    }

    /**
     * Update a department
     */
    @PutMapping("/{id}")
    public ResponseEntity<?> updateDepartment(@PathVariable String id, @RequestBody Department department) {
        try {
            Optional<Department> existingDept = departmentRepository.findById(id);
            if (!existingDept.isPresent()) {
                return ResponseEntity.notFound().build();
            }

            Department existing = existingDept.get();
            existing.setName(department.getName());
            existing.setLocation(department.getLocation());

            Department savedDepartment = departmentRepository.save(existing);
            return ResponseEntity.ok(savedDepartment);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error updating department");
        }
    }

    /**
     * Delete a department
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteDepartment(@PathVariable String id) {
        try {
            Optional<Department> dept = departmentRepository.findById(id);
            if (!dept.isPresent()) {
                return ResponseEntity.notFound().build();
            }

            departmentRepository.deleteById(id);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error deleting department");
        }
    }

    private Map<String, Object> departmentToMap(Department dept) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", dept.getId());
        map.put("name", dept.getName());
        map.put("location", dept.getLocation());
        return map;
    }
    
    /**
     * Get all unique locations (for new simplified structure)
     */
    @GetMapping("/locations")
    public ResponseEntity<List<String>> getAllLocations() {
        try {
            List<String> locations = departmentRepository.findAll().stream()
                    .map(Department::getLocation)
                    .filter(location -> location != null && !location.trim().isEmpty())
                    .distinct()
                    .sorted()
                    .collect(Collectors.toList());
            
            return ResponseEntity.ok(locations);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get departments by location (for new simplified structure)
     */
    @GetMapping("/by-location/{location}")
    public ResponseEntity<List<Department>> getDepartmentsByLocation(@PathVariable String location) {
        try {
            List<Department> departments = departmentRepository.findAll().stream()
                    .filter(dept -> location.equalsIgnoreCase(dept.getLocation()))
                    .collect(Collectors.toList());
            
            return ResponseEntity.ok(departments);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}
