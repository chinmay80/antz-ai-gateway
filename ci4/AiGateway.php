<?php
// app/Controllers/Api/AiGateway.php
// The gateway calls this with the user's own bearer token.
// Reuse whatever your existing API auth filter already does; this
// controller only shapes the response the gateway needs.
//
// Route (app/Config/Routes.php):
//   $routes->get('api/ai/whoami', 'Api\AiGateway::whoami', ['filter' => 'YOUR_EXISTING_AUTH_FILTER']);

namespace App\Controllers\Api;

use App\Controllers\BaseController;

class AiGateway extends BaseController
{
    public function whoami()
    {
        // TODO: replace with however your auth filter exposes the current user
        $user = service('auth')->user();
        if (! $user) {
            return $this->response->setStatusCode(401)->setJSON(['message' => 'Unauthorized']);
        }

        // TODO: replace with your existing "sites this user can access" query
        $sites = model('SiteModel')->getSitesForUser($user->user_id);

        return $this->response->setJSON([
            'data' => [
                'user_id'    => (int) $user->user_id,
                'name'       => $user->user_first_name . ' ' . $user->user_last_name,
                'role'       => $user->role_name,
                'zoo_id'     => (int) $user->zoo_id,
                'zoo_name'   => $user->zoo_name,
                'site_ids'   => array_map('intval', array_column($sites, 'site_id')),
                'site_names' => array_column($sites, 'site_name'),
            ],
        ]);
    }
}
