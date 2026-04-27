import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../../p1_usuarios/auth.service';

/**
 * Guard que verifica el rol del usuario.
 * Uso: canActivate: [roleGuard('admin'), roleGuard('taller')]
 */
export function roleGuard(...allowedRoles: string[]): CanActivateFn {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);

    if (!auth.isLoggedIn()) {
      void router.navigate(['/login']);
      return false;
    }

    const role = sessionStorage.getItem('user_role');
    if (role && allowedRoles.includes(role)) {
      return true;
    }

    void router.navigate(['/home']);
    return false;
  };
}
