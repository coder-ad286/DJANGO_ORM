from .serializer import CategorySerializer, PostValueSerializer,CommentSerializer, PostSerializer, LikeSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Category, Comment, Post, Like, STATUS
from django.db.models import Q

"""
THE ACTION DECORATORS INDICATES ITS END POINT
METHOD NAME EQUAL TO URL
IF DETAIL FALSE , NO EXPECTED THE PARAMETER,
IF DETAIL TRUE ,  EXPECTED THE PARAMETER URL LIKE BASEURL/PARAMTER/CURRENT METHOD NAME ,
"""


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=False, methods=["POST"])
    def create_data(self, req):

        serializer = self.serializer_class(data=req.data or None)
        serializer.is_valid(raise_exception=True)

        title_data = serializer.validated_data.get("title")
        slug_data = serializer.validated_data.get("slug")
        description_data = serializer.validated_data.get("description")

        obj = Category.objects.create(
            title=title_data,
            slug=slug_data,
            description=description_data
        )

        serializer = self.serializer_class(obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"])
    def save_data(self, req):

        serializer = self.serializer_class(data=req.data or None)
        serializer.is_valid(raise_exception=True)

        title_data = serializer.validated_data.get("title")
        slug_data = serializer.validated_data.get("slug")
        description_data = serializer.validated_data.get("description")

        obj = Category()
        obj.title = title_data
        obj.slug = slug_data
        obj.description = description_data
        obj.save()

        serializer = self.serializer_class(obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"])
    def get_or_create_data(self, req):
        serializer = self.serializer_class(data=req.data or None)
        serializer.is_valid(raise_exception=True)

        title_data = serializer.validated_data.get("title")
        slug_data = serializer.validated_data.get("slug")

        obj, _ = Category.objects.get_or_create(
            title=title_data,
            slug=slug_data
        )

        serializer = self.serializer_class(obj)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"])
    def bulk_create_data(self, req):

        serializer = self.serializer_class(data=req.data or None, many=True)
        serializer.is_valid(raise_exception=True)

        new_data = []
        for row in serializer.validated_data:
            new_data.append(
                Category(
                    title=row["title"],
                    slug=row["slug"],
                    description=row["description"]
                )
            )

        Category.objects.bulk_create(new_data)
        return Response("Data Created Successfully...!", status=status.HTTP_201_CREATED)


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    # LIKE APPEND ADD CATEGORIES TO EXITING CATEGORIES LIST
    @action(detail=True, methods=["PATCH"])
    def add_category(self, req, pk):
        post = Post.objects.filter(id=pk).first()
        categories_data = req.data.get("ids")

        categories_data = set(categories_data)
        post.category.add(*categories_data)  # THIS ONLY ADD UNIQUE ELEMENT

        serializer = self.serializer_class(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # DELETE EXITING CATEGORIES LIST ADD CATEGORIES TO NEW LIST
    @action(detail=True, methods=["PATCH"])
    def set_category(self, req, pk):
        post = Post.objects.filter(id=pk).first()
        categories_data = req.data.get("ids")

        # REMOVE DUPLICATE FROM LIST AND CONVERT TO SET
        categories_data = set(categories_data)
        post.category.set(categories_data)

        serializer = self.serializer_class(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @action(detail=True,methods=["PUT"])
    # def update_data(self,req,pk):
    #     post =Post.objects.get(id=pk)
    #     serializer = self.serializer_class(post,data=req.data,partial=True)
    #     # WE CAN ALSO USE post.update(....) BUT IT ONLY UPDATE EXPLICITLY GIVEN FIELDS , NOT ALL FIELDS
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data,status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["PUT"])
    def update_data(self, req, pk):
        try:
            summary_data = req.data["summary"]
            content_data = req.data["content"]
        except:
            return Response({"success": False, "message": "All Fields Are Required...!"}, status=status.HTTP_400_BAD_REQUEST)
        post = Post.objects.filter(id=pk)
        post.update(
            summary=summary_data,
            content=content_data
        )
        return Response({"message": "Summary & Content Updated Successfully...!"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["PUT"])
    def update_or_create_data(self, req):
        category_data = set(req.data.get("category"))
        summary_data = req.data.get("summary")
        title_data = req.data.get("title")
        content_data = req.data.get("content")
        author = 1

        post, _ = Post.objects.update_or_create(
            title=title_data,  # FILTER
            defaults={
                "summary": summary_data,
                "content": content_data,
                "author_id": author,

            }
        )

        post.category.set(category_data)
        return Response({"message": "Post Updated Successfully...!"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"])
    def bulk_update(self, req):
        ids = req.data.get("ids")
        if not ids:
            return Response({"success": False, "message": "Ids Field Is Required...!"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Post.objects.filter(id__in=ids)

        for obj in queryset:
            obj.status = STATUS.PUBLISH.value

        Post.objects.bulk_update(queryset, ["status"])
        return Response({"message": "Post Updated Bulk Successfully...!"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["GET"])
    def get_all(self, req):
        queryset = Post.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def get_one(self, req):
        slug = req.GET.get("slug")  # USED TO GET PARAMS IN GET REQUEST
        try:
            # THIS WILL THROW ERROR WHEN MAULTIPLE OBJECTS EXISTS AND NO OBJECT EXISTS SO IT ONLY ACCEPTS ONE OBJECT
            obj = Post.objects.get(slug=slug)
        except Post.MultipleObjectsReturned:
            return Response({"message": "Multiple Objects Found"}, status=status.HTTP_400_BAD_REQUEST)

        except Post.DoesNotExist:
            return Response({"message": "No Object Found"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def get_filter(self, req):
        id = req.GET.get("id")
        obj = Post.objects.filter(id=id).first()
        serializer = self.serializer_class(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def exclude_fiter(self, req):
        id = req.GET.get("id")
        # EXCLUDE USED TO SKIP DATA WE DONT WANT
        # ALSO WE WILL SEPECIFY IN METHOD CHAINING
        queryset = Post.objects.filter(status="1").exclude(id=id)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def limit_data(self, req):
        queryset = Post.objects.all()[2:4]  # FILTER WORKED BY LIST OPERATION
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def lookup_filter(self, req):
        ids = req.GET.get("ids")
        ids = ids.split(",")
        print(ids)
        # LOOUP FIELD THIS EQUAL TO SQL "LIKE"
        queryset = Post.objects.filter(id__in=ids)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def order_by_data(self, req):
        # DESCENDING ORDER ADD "-" IN PREFIX
        # ALSO WE CAN GIVE MULTIPLE FILEDS TO ORDER
        queryset = Post.objects.all().order_by("-id")
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def distinct_data(self, req):
        queryset = (Post.objects.all().filter(
            category__id__in=[1, 2]).distinct())
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def deep_filter_data(self, req):
        queryset = Post.objects.all().filter(
            category__id__in=[2, 3]).distinct()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def get_values(self, req, pk):
        # EXTRACT NEEDED FIELDS FROM DB
        # IN SAME KEY-VALUE PAIR
        queryset = Post.objects.filter(pk=pk).values("id","title","slug")
        serializer = PostValueSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"])
    def get_values_list(self, req, pk):
        # EXTRACT NEEDED FIELDS FROM DB
        # IN THIS WITHOUT KEYS AND RETURN LIST OF VALUES
        # queryset = Post.objects.filter(pk=pk).values_list("id","title","slug")
        queryset = Post.objects.all().values_list("id",flat=True)
        # USED TO CONVERT ALL IDS INTO ONE LIST FLAT DOESN'T SUPPORT MULTIPLE VALUES
        return Response(queryset, status=status.HTTP_200_OK)
    
    @action(detail=True,methods=["GET"])
    def q_filter(self,req,pk,*args,**kwargs):
        # queryset = Post.objects.filter(Q(pk=pk)) # WITH Q
        # queryset = Post.objects.filter(~Q(pk=pk)) # WITH NEGATION
        # queryset = Post.objects.filter(Q(pk=pk)| Q(author=pk) ) # WITH OR
        # queryset = Post.objects.filter(Q(pk=pk) & Q(author=pk) ) # WITH AND
        # queryset = Post.objects.filter(~Q(pk=pk) & Q(author=pk) ) # WITH NEGATION & AND
        queryset = Post.objects.filter(~Q(pk=pk) & Q(author=pk) ) # WITH NESTED Q M
        serializer = self.serializer_class(queryset, many=True) 
        return Response(serializer.data, status=status.HTTP_200_OK)



