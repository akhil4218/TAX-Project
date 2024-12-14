import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterModule, Router } from '@angular/router';

@Component({
  selector: 'app-welcome',
  imports: [RouterModule, CommonModule],
  templateUrl: './welcome.component.html',
  styleUrl: './welcome.component.scss',
})

export class WelcomeComponent {
  isLoggedIn: boolean = false;
  username: string = '';
  activeTab: string = 'tab-1';
  logoutMessage: string = ''; 

  constructor(private router: Router) {}

  ngOnInit(): void {
    // Check if the user is logged in by checking localStorage
    const storedUsername = localStorage.getItem('username');
    if (storedUsername) {
      this.isLoggedIn = true;
      this.username = storedUsername;
    }
  }


  logout(): void {
    // Clear user login state from localStorage
    localStorage.removeItem('username');
    this.isLoggedIn = false;
    this.username = '';
    this.logoutMessage = 'You have successfully logged out!'; 
    setTimeout(() => {
      this.router.navigate(['/welcome']); 
      this.logoutMessage = '';  
    }, 2000);  
  }
  showContent(tabId: string): void {
    this.activeTab = tabId;
  }
}
