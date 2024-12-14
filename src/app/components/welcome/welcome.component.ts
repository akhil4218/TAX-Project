
import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterModule, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-welcome',
  imports: [RouterModule, CommonModule],
  templateUrl: './welcome.component.html',
  styleUrl: './welcome.component.scss',
})
export class WelcomeComponent {
  activeTab: string = 'tab-1'

  constructor() {}


  showContent(tabId: string): void {
    this.activeTab = tabId;
  }
  
}

