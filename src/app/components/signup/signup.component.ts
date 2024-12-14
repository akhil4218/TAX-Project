import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-signup',
  imports: [CommonModule, HttpClientModule, RouterModule, FormsModule],
  templateUrl: './signup.component.html',
  styleUrl: './signup.component.scss',
})
export class SignupComponent {
  username = '';
  email = ''; // Added email property
  password = '';
  message = '';

  constructor(private http: HttpClient, private router: Router) {}

  onSignup() {
    const payload = {
      username: this.username,
      email: this.email, // Include email in payload
      password: this.password,
      role: "user",
    };

    this.http.post('http://127.0.0.1:5000/signup', payload).subscribe(
      (response: any) => {
        this.message = 'Signup successful!';
        this.router.navigate(['/login']); // Redirect to login page
      },
      (error: any) => {
        // Improved error handling
        if (error.status === 400) {
          const errorMessage = error.error.error || 'Signup failed!';
          this.message = errorMessage;
        } else {
          this.message = 'An unexpected error occurred. Please try again later.';
        }
      }
    );
  }
}
