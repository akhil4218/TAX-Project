import { Routes } from '@angular/router';
import { WelcomeComponent } from './components/welcome/welcome.component';
import { SignupComponent } from './components/signup/signup.component';
import { LoginComponent } from './components/login/login.component';
import { TicketsComponent } from './components/tickets/tickets.component';

export const routes: Routes = [
  { path: '', redirectTo: 'welcome', pathMatch: 'full' }, // Redirect empty route
  { path: 'welcome', component: WelcomeComponent },
  { path: 'signup', component: SignupComponent },
  { path: 'login', component: LoginComponent },
  { path: 'tickets', component: TicketsComponent },
  { path: '**', redirectTo: 'welcome' }, // Fallback route for undefined paths
];
