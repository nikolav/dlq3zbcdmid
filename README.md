Sat Mar 16 22:09:17 UTC 2024
3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]

#recepies
.table
  id: ID
  title: string
  description: string
  instructions: string
  ingredients: Record<nadme: string, qty: string>
  preparation_time: number minutes
  servings: number; for how many people
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

