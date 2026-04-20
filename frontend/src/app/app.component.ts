import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from './core/auth.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  title = 'RutAIGeoProxi';
  private readonly auth = inject(AuthService);
  menuOpen = false;

  isLoggedIn(): boolean {
    return this.auth.isLoggedIn();
  }

  get userRole(): string | null {
    return sessionStorage.getItem('user_role');
  }

  toggleMenu(): void {
    this.menuOpen = !this.menuOpen;
  }

  logout(): void {
    this.auth.logout();
    this.menuOpen = false;
  }
}
