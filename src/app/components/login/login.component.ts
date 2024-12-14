import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  imports: [FormsModule, CommonModule, HttpClientModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  constructor(private http: HttpClient, private router: Router) {}

  email: string = ''; // Changed to email instead of username
  password: string = '';
  errorMessage: string = '';

  onLogin(event: any) {
    event.preventDefault(); // Prevent form from reloading the page
    console.log('Form submitted:');
    console.log(`${this.email} ${this.password}`);

    const payload = { email: this.email, password: this.password }; // Updated payload to use email
    console.log('Payload: ', payload);

    this.http.post('http://127.0.0.1:5000/login', payload).subscribe(
      (response: any) => {
        if (response.message === 'Login successful') {
          // Store the username (from response) and token if needed
          localStorage.setItem('username', response.username);
          localStorage.setItem('access_token', response.access_token); // Store token
          this.router.navigate(['/']); // Redirect to home after successful login
        } else {
          this.errorMessage = 'Invalid credentials!';
        }
      },
      (error) => {
        // Handle error cases such as network issues or invalid login
        this.errorMessage = 'Something went wrong! Please try again.';
      }
    );
  }
}
