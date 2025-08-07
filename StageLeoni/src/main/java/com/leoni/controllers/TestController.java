package com.leoni.controllers;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/test")
@CrossOrigin(origins = "*")
public class TestController {
    
    @GetMapping("/ping")
    public ResponseEntity<Map<String, Object>> ping() {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "Test controller is working");
        response.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(response);
    }
    
    @PostMapping("/echo")
    public ResponseEntity<Map<String, Object>> echo(@RequestBody Map<String, String> data) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "Echo successful");
        response.put("received", data);
        response.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(response);
    }
}