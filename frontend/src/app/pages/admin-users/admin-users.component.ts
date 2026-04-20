import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService, Me } from '../../core/auth.service';

@Component({
  selector: 'app-admin-users',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-users.component.html',
  styleUrls: ['./admin-users.component.css'],
})
export class AdminUsersComponent implements OnInit {
  private readonly auth = inject(AuthService);

  users: Me[] = [];
  loading = true;
  error = '';
  editingUser: Me | null = null;
  newPermissionsStr = '';

  roles = ['admin', 'taller', 'cliente'];

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.loading = true;
    this.auth.listUsers().subscribe({
      next: (data) => {
        this.users = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Error al cargar usuarios';
        this.loading = false;
      },
    });
  }

  changeRole(user: Me, newRole: string): void {
    if (user.rol === newRole) return;
    
    this.auth.updateUserRole(user.id, newRole).subscribe({
      next: (updated) => {
        const idx = this.users.findIndex((u) => u.id === user.id);
        if (idx !== -1) this.users[idx] = updated;
      },
      error: (err) => {
        alert(err.error?.detail || 'Error al actualizar rol');
      },
    });
  }

  openPermissions(user: Me): void {
    this.editingUser = user;
    this.newPermissionsStr = JSON.stringify(user.permisos || {}, null, 2);
  }

  savePermissions(): void {
    if (!this.editingUser) return;
    
    try {
      const perms = JSON.parse(this.newPermissionsStr);
      this.auth.updateUserPermissions(this.editingUser.id, perms).subscribe({
        next: (updated) => {
          const idx = this.users.findIndex((u) => u.id === this.editingUser!.id);
          if (idx !== -1) this.users[idx] = updated;
          this.editingUser = null;
        },
        error: (err) => {
          alert('Error al guardar permisos');
        },
      });
    } catch (e) {
      alert('JSON de permisos inválido');
    }
  }
}
