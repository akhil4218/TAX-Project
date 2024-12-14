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
  username: string = '';
  password: string = '';
  errorMessage: string = '';
  onLogin(event: any) {
    console.log('Form submitted: ');
    console.log(`${this.username} ${this.password}`);

    const payload = { username: this.username, password: this.password };
    console.log('Payload: ', payload);
    this.http.post('http://127.0.0.1:5000/login', payload).subscribe(
      (response: any) => {
        if (response.message === 'Login successful') {
          localStorage.setItem('username', this.username);
          this.router.navigate(['/']);
        } else {
          this.errorMessage = 'Invalid credentials!';
        }
      },
      (error) => {
        this.errorMessage = 'Something went wrong!';
      }
    );
  }
}
