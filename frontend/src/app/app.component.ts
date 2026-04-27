import { Component, inject, OnInit } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from './modules/p1_usuarios/auth.service';
import { WebSocketService } from './modules/shared/websocket.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit {
  title = 'RutAIGeoProxi';
  private readonly auth = inject(AuthService);
  private readonly ws = inject(WebSocketService);
  
  menuOpen = false;
  isDarkTheme = true;
  notifications: any[] = [];
  unreadCount = 0;
  showNotifications = false;

  ngOnInit() {
    this.isDarkTheme = localStorage.getItem('theme') !== 'light';
    this.applyTheme();
    if (this.isLoggedIn()) {
      this.initNotifications();
    }
  }

  initNotifications() {
    const token = this.auth.token;
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const userId = parseInt(payload.sub, 10);
        if (userId) {
          this.ws.connectNotifications(userId).subscribe((notif) => {
            this.notifications.unshift(notif);
            this.unreadCount++;
          });
        }
      } catch (e) {
        console.error('Error parsing token for notifications', e);
      }
    }
  }

  toggleNotifications() {
    this.showNotifications = !this.showNotifications;
    if (this.showNotifications) {
      this.unreadCount = 0;
    }
  }

  toggleTheme() {
    this.isDarkTheme = !this.isDarkTheme;
    localStorage.setItem('theme', this.isDarkTheme ? 'dark' : 'light');
    this.applyTheme();
  }

  private applyTheme() {
    document.body.classList.toggle('light-theme', !this.isDarkTheme);
  }

  isLoggedIn(): boolean {
    return this.auth.isLoggedIn();
  }

  get userRole(): string | null {
    return this.auth.getUserRole();
  }

  toggleMenu(): void {
    this.menuOpen = !this.menuOpen;
  }

  logout(): void {
    this.auth.logout();
    this.menuOpen = false;
  }
}
