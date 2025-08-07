package com.leoni.dto;

public class SimpleAuthRequest {
    
    private String username;
    private String password;
    
    public SimpleAuthRequest() {}
    
    public SimpleAuthRequest(String username, String password) {
        this.username = username;
        this.password = password;
    }
    
    public String getUsername() {
        return username;
    }
    
    public void setUsername(String username) {
        this.username = username;
    }
    
    public String getPassword() {
        return password;
    }
    
    public void setPassword(String password) {
        this.password = password;
    }
    
    @Override
    public String toString() {
        return "SimpleAuthRequest{username='" + username + "', password='[PROTECTED]'}";
    }
}