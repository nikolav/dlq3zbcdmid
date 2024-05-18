# Reverse proxy nginx letsencrypt
# https://github.com/christianlempa/videos/tree/main/nginx-reverseproxy

.recepies
  #public
    id: ID
    title: string
    description: string
    instructions: string
    ingredients: Record<nadme: string, qty: string>
    preparation_time: number minutes
    servings: number; how many people
    category|dish: string
      # salate, predjelo, glavno jelo, čorbe, dezert, peciva, sirova hrana
    meta: json
      .calories
      .health: low sug low fat, protein rich..
      .cuisine: french, italian..
    user_id: ID
    created_at: time
    updated_at: time

  # virtual  
    user: User
