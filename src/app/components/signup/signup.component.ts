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
  password = '';
  message = '';

  constructor(private http: HttpClient, private router: Router) {}

  onSignup() {
    const payload = { username: this.username, password: this.password };

    this.http.post('http://127.0.0.1:5000/signup', payload).subscribe(
      (response) => {
        this.message = 'Signup successful!';
        this.router.navigate(['/login']);
      },
      (error) => {
        this.message = 'Signup failed!';
      }
    );
  }
}
