# Plugsbox - Plugin NetBox

Plugin pour l'administration des prises réseau sur le campus.

## Environnement de Développement

Ce projet utilise Docker et Docker Compose pour fournir un environnement de développement NetBox cohérent et reproductible. Le `Makefile.mk` à la racine simplifie la gestion de cet environnement.

### Prérequis

*   Docker
*   Docker Compose
*   `make`

### Configuration

Les versions de NetBox et Python peuvent être configurées au début du fichier `Makefile.mk`:

```makefile
PYTHON_VER?=3.12
NETBOX_VER?=v4.3.3
```

### Premier Lancement

Pour lancer l'environnement pour la première fois, suivez ces étapes :

1.  **Construire les images Docker :**
    Cette commande construit l'image NetBox personnalisée avec les versions de Python et NetBox spécifiées.

    ```bash
    make cbuild
    ```

2.  **Lancement initial et vérification :**
    Cette commande démarre tous les services en avant-plan (`foreground`). Vous pourrez voir les logs en direct pour vérifier que tout se lance correctement.

    ```bash
    make debug
    ```

    Une fois que vous voyez que les services sont démarrés et stables (en particulier NetBox), vous pouvez arrêter le processus avec `Ctrl+C`.

3.  **Démarrer en arrière-plan :**
    Maintenant, lancez les services en mode détaché pour qu'ils tournent en arrière-plan.

    ```bash
    make start
    ```

4.  **Créer un super-utilisateur :**
    Pour pouvoir vous connecter à l'interface web de NetBox, créez un compte administrateur.

    ```bash
    make adduser
    ```
    Suivez les instructions pour définir un nom d'utilisateur, une adresse e-mail et un mot de passe.

L'environnement est maintenant prêt ! Vous pouvez accéder à NetBox à l'adresse http://localhost:8000.

### Commandes courantes

Voici les commandes `make` les plus utiles pour gérer l'environnement de développement :

*   `make start`: Démarre les conteneurs en arrière-plan.
*   `make stop`: Arrête les conteneurs.
*   `make debug`: Démarre les conteneurs en avant-plan pour le débogage.
*   `make destroy`: **ATTENTION :** Arrête et supprime les conteneurs ET les volumes de données (comme la base de données). Utile pour repartir de zéro.
*   `make nbshell`: Ouvre un shell interactif NetBox (`manage.py nbshell`).
*   `make adduser`: Lance la création d'un super-utilisateur.
*   `make migrations`: Crée les fichiers de migration pour votre plugin.

### Packaging du Plugin

Pour construire le package Python pour la distribution :

```bash
make pbuild
```