from multiprocessing import context
from django.shortcuts import render, reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from agents.mixins import OrganisorAndLoginRequiredMixin

from .models import (Lead, Category)
from .forms import( LeadModelForm,
                    CustomUserCreationForm,
                    AssignAgentForm,
                    LeadCategoryUpdateForm,
                    CategoryModelForm,
                )

#views coded with class base views

class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

class LandingView(generic.TemplateView):
    template_name = "landing.html"


class LeadListView(OrganisorAndLoginRequiredMixin,generic.ListView):
    template_name = "lead_list.html"
    context_object_name = "leads"

    def get_queryset(self):
        user = self.request.user
 
        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation=user.userprofile,
                agent__isnull=False
                )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation,
                 agnt__isnull=False
                 )

            queryset = queryset.filter(agent__user= user)
        return queryset
    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(LeadListView, self).get_context_data(**kwargs)
        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation=user.userprofile,
                agent__isnull=True
                )
            context.update({
                "unassigned_leads": queryset
                })
        return context
    

class LeadDetailView(OrganisorAndLoginRequiredMixin,generic.DetailView):
    template_name = "lead_detail.html"
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)

            queryset = queryset.filter(agent__user= user)
        return queryset


class LeadCreateView(OrganisorAndLoginRequiredMixin,generic.CreateView):
    template_name = "lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("leads:lead-list")
    
    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        return super(LeadCreateView, self).form_valid(form)

class LeadUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "lead_update.html"
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile)

    def get_success_url(self):
        return reverse("leads:lead-list")

class LeadDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "lead_delete.html"

    def get_success_url(self):
        return reverse("leads:lead-list")

    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile)


class AssignAgentView(OrganisorAndLoginRequiredMixin, generic.FormView):
    template_name = 'assign_agent.html'
    form_class = AssignAgentForm
    
    def get_form_kwargs(self, **kwargs) :
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_success_url(self) : 
        return reverse("leads:lead-list")

    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent =agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)




class CategoryListView(LoginRequiredMixin, generic.ListView):

    template_name = "category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation=user.userprofile
                )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation
                )

        context.update({
            "unassigned_lead_count":queryset.filter(category__isnull=True).count()
        })
        return context

    def get_queryset(self):
        user = self.request.user
 
        if user.is_organisor:
            queryset = Category.objects.filter(
                organisation=user.userprofile
                )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
                )
        return queryset



class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        leads = self.get_object().leads.all()
        context.update({
            "leads": leads
        })
        return context


    def get_queryset(self):
        user = self.request.user
 
        if user.is_organisor:
            queryset = Category.objects.filter(
                organisation=user.userprofile
                )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
                )
        return queryset

class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        #queryset of leads for entire organisation
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation = user.agent.organisation)
            #filter for the agent that is logged in.
            queryset = queryset.filter(agent__user=user)
        return queryset
    def get_success_url(self) :
        return reverse("leads:lead-detail" ,kwargs={"pk": self.get_object().id})

class CategoryCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "category_create.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("leads:category-list")
    
    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        return super(CategoryCreateView, self).form_valid(form)

class CategoryUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "category_update.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("leads:category-list")
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organisor: 
            queryset = Category.objects.filter(
                organisation = user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation = user.agent.organisation
            )
        return queryset

class CategoryDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "category_delete.html"

    def get_success_url(self):
        return reverse("leads:category-list")
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organisor: 
            queryset = Category.objects.filter(
                organisation = user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation = user.agent.organisation
            )
        return queryset
