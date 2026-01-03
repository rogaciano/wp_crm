"""
Permissões customizadas para hierarquia de Canais
"""
from rest_framework import permissions


class HierarchyPermission(permissions.BasePermission):
    """
    Permissão baseada na hierarquia de vendas:
    - Admin: vê tudo
    - Responsável: vê dados do seu canal
    - Vendedor: vê apenas seus dados
    """
    
    def has_permission(self, request, view):
        # Usuário deve estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin tem acesso total
        if request.user.perfil == 'ADMIN':
            return True
        
        # Responsável e Vendedor precisam de canal
        if request.user.perfil in ['RESPONSAVEL', 'VENDEDOR']:
            return request.user.canal is not None
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Verifica se o usuário pode acessar um objeto específico
        """
        user = request.user
        
        # Admin tem acesso total
        if user.perfil == 'ADMIN':
            return True
        
        # Vendedor: só seus próprios objetos E deve estar em funil que tem acesso
        if user.perfil == 'VENDEDOR':
            owner_match = getattr(obj, 'proprietario', None) == user
            funil_match = True
            if hasattr(obj, 'funil') and obj.funil:
                funil_match = user.funis_acesso.filter(id=obj.funil.id).exists()
            return owner_match and funil_match
        
        # Responsável: objetos do seu canal E de funis que tem acesso
        if user.perfil == 'RESPONSAVEL':
            # Canal match: via campo direto ou via proprietário
            canal_match = False
            if hasattr(obj, 'canal') and obj.canal:
                canal_match = (obj.canal == user.canal)
            elif hasattr(obj, 'proprietario') and obj.proprietario.canal:
                canal_match = (obj.proprietario.canal == user.canal)
            
            # Funil match
            funil_match = True
            if hasattr(obj, 'funil') and obj.funil:
                funil_match = user.funis_acesso.filter(id=obj.funil.id).exists()
                
            return canal_match and funil_match
        
        return False


class IsAdminUser(permissions.BasePermission):
    """
    Permite acesso apenas para usuários com perfil ADMIN
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.perfil == 'ADMIN'
        )


class IsResponsavelOrAdmin(permissions.BasePermission):
    """
    Permite acesso para Responsável de Canal ou Admin
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.perfil in ['ADMIN', 'RESPONSAVEL']
        )
