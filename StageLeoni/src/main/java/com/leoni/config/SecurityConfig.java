package com.leoni.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfigurationSource;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Autowired
    private CorsConfigurationSource corsConfigurationSource;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .cors(cors -> cors.configurationSource(corsConfigurationSource))
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(authz -> authz
                // Allow all API endpoints for admin panel
                .requestMatchers("/api/**").permitAll()
                // Allow actuator endpoints
                .requestMatchers("/actuator/**").permitAll()
                // Allow health check endpoints
                .requestMatchers("/health/**").permitAll()
                // Allow uploads directory
                .requestMatchers("/uploads/**").permitAll()
                // Allow any other requests
                .anyRequest().permitAll()
            );

        return http.build();
    }
}